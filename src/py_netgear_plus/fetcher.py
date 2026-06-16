"""HTML page retrieval classes."""

import json
import logging
import re
from contextlib import suppress
from pathlib import Path
from typing import Any

import requests
import requests.cookies
from lxml import html
from requests import Response

from py_netgear_plus.models import (
    MODELS,
    AutodetectedSwitchModel,
    InvalidCryptFunctionError,
    SwitchModelNotDetectedError,
)
from py_netgear_plus.netgear_crypt import hex_hmac_md5, merge_hash

DEFAULT_PAGE = "index.htm"
URL_REQUEST_TIMEOUT = 15
status_code_ok = requests.codes.ok
status_code_not_found = requests.codes.not_found
status_code_no_response = requests.codes.no_response
status_code_unauthorized = requests.codes.unauthorized

_LOGGER = logging.getLogger(__name__)


def _normalize_model_identifier(value: Any) -> str:
    """Return a compact comparable model identifier."""
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())


def _iter_json_values(value: Any):
    """Yield scalar values from a nested JSON-like structure."""
    if isinstance(value, dict):
        for nested_value in value.values():
            yield from _iter_json_values(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from _iter_json_values(nested_value)
    elif value is not None:
        yield value


class PageFetcherConnectionError(Exception):
    """Connection reset while requesting page."""


class LoginFailedError(Exception):
    """Invalid credentials."""


class NotLoggedInError(Exception):
    """Not logged in."""


class PageNotLoadedError(Exception):
    """Failed to load the page."""


class EmptyTemplateParameterError(Exception):
    """None of the models passed the tests."""


class BaseResponse:
    """Base class for response objects."""

    def __init__(self) -> None:
        """Initialize BaseResponse Object."""
        self.status_code = status_code_not_found
        self.content = b""
        self.cookies = requests.cookies.RequestsCookieJar()

    def __bool__(self) -> bool:
        """Return True if status code is 200."""
        return self.status_code == status_code_ok


class PageFetcher:
    """Class to fetch html pages from switch (or file)."""

    def __init__(self, host: str) -> None:
        """Initialize PageFetcher Object."""
        self.host = host
        # cached login page response
        self._login_page_response = None
        self._password_hash = None

        # login cookie
        self._cookie_name = None
        self._cookie_content = None

        # bearer token (JSON REST API switches)
        self._bearer_token = None

        # offline mode settings
        self.offline_mode = False
        self.offline_path_prefix = ""

    def turn_on_offline_mode(self, path_prefix: str) -> None:
        """Turn on offline mode."""
        self.offline_mode = True
        self.offline_path_prefix = path_prefix

    def turn_on_online_mode(self) -> None:
        """Turn on online mode."""
        self.offline_mode = False

    def check_login_url(self, switch_model: type[AutodetectedSwitchModel]) -> bool:
        """Check and cache login page."""
        templates = switch_model.AUTODETECT_TEMPLATES
        for template in templates:
            url = template["url"].format(ip=self.host)
            if self.offline_mode:
                _LOGGER.debug(
                    "[PageFetcher.check_login_url] reading %s from file.", url
                )
                self._login_page_response = self.get_page_from_file(url)
            else:
                method = template["method"]
                allow_redirects = False
                timeout = URL_REQUEST_TIMEOUT
                _LOGGER.debug(
                    "[PageFetcher.check_login_url] calling request for %s %s"
                    " with allow_directs=%s, timeout=%d",
                    method.upper(),
                    url,
                    allow_redirects,
                    timeout,
                )
                with suppress(
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.ChunkedEncodingError,
                ):
                    self._login_page_response = requests.request(
                        method, url, allow_redirects=allow_redirects, timeout=timeout
                    )

            if self.has_ok_status(self._login_page_response):
                return True
        message = f"Failed to load any page of templates: {templates}"
        raise PageNotLoadedError(message)

    def get_login_page_response(self) -> Response | BaseResponse | None:
        """Return cached login page."""
        return self._login_page_response

    def clear_login_page_response(self) -> None:
        """Return cached login page."""
        self._login_page_response = None
        self._password_hash = None

    def get_cookie(self) -> tuple[str | None, str | None]:
        """Get cookie."""
        if self._cookie_name and self._cookie_content:
            return (self._cookie_name, self._cookie_content)
        return (None, None)

    def set_cookie(self, cookie_name: str, cookie_content: str) -> None:
        """Set cookie."""
        self._cookie_name = cookie_name
        self._cookie_content = cookie_content

    def clear_cookie(self) -> None:
        """Clear cookie."""
        self._cookie_name = None
        self._cookie_content = None

    def set_bearer_token(self, token: str) -> None:
        """Set Bearer token for JSON REST API authentication."""
        self._bearer_token = token

    def has_bearer_token(self) -> bool:
        """Return True if a Bearer token is set."""
        return self._bearer_token is not None

    def clear_bearer_token(self) -> None:
        """Clear Bearer token."""
        self._bearer_token = None

    def _parse_json_body(self, response: Response | BaseResponse) -> dict[str, Any] | None:
        """Return response JSON when it is a dictionary."""
        try:
            body = response.json()
        except (AttributeError, ValueError):
            return None
        if not isinstance(body, dict):
            return None
        return body

    def _prepare_json_response(
        self, url: str, response: Response | BaseResponse, request_data: Any = None
    ) -> None:
        """Prepare JSON API responses for login retry and model detection."""
        body = self._parse_json_body(response)
        if body is None:
            return

        # Some MS-series firmware returns HTTP 200 with an error payload when an
        # endpoint needs authentication. Treat that as unauthorized so callers
        # retry after JSON REST login.
        err_code = body.get("errCode")
        if request_data is None and not self._bearer_token and err_code not in (
            None,
            0,
            "0",
        ):
            _LOGGER.debug(
                "[PageFetcher.json_request] JSON API endpoint %s returned errCode=%s "
                "without a bearer token; retrying after login.",
                url,
                err_code,
            )
            response.status_code = status_code_unauthorized
            return

        self._normalise_json_status_model(url, response, body)

    def _normalise_json_status_model(
        self, url: str, response: Response | BaseResponse, body: dict[str, Any]
    ) -> None:
        """Normalise JSON REST status model info for autodetection."""
        if "/api/system/status" not in url:
            return

        system_info = body.get("systemInfo")
        if not isinstance(system_info, dict):
            system_info = {}
            body["systemInfo"] = system_info

        candidate_values = [
            system_info.get("modelNumber"),
            system_info.get("modelName"),
            system_info.get("productName"),
            body.get("modelNumber"),
            body.get("modelName"),
            body.get("productName"),
            body.get("deviceName"),
        ]
        candidate_values.extend(_iter_json_values(body))

        json_api_models = [
            mdl_cls()
            for mdl_cls in MODELS
            if getattr(mdl_cls(), "API_TYPE", "") == "json_rest"
        ]
        for candidate_value in candidate_values:
            normalized_candidate = _normalize_model_identifier(candidate_value)
            if not normalized_candidate:
                continue
            for model in json_api_models:
                normalized_model = _normalize_model_identifier(model.MODEL_NAME)
                if normalized_model and normalized_model in normalized_candidate:
                    if system_info.get("modelNumber") != model.MODEL_NAME:
                        _LOGGER.debug(
                            "[PageFetcher.json_request] Normalized JSON REST model "
                            "value %r to %s for IP=%s",
                            candidate_value,
                            model.MODEL_NAME,
                            self.host,
                        )
                    system_info["modelNumber"] = model.MODEL_NAME
                    if isinstance(response, Response):
                        response._content = json.dumps(  # noqa: SLF001
                            body, separators=(",", ":")
                        ).encode("utf-8")
                    return

        _LOGGER.debug(
            "[PageFetcher.json_request] JSON REST status response for IP=%s did "
            "not contain a known model. top_level_keys=%s system_info_keys=%s",
            self.host,
            sorted(body.keys()),
            sorted(system_info.keys()),
        )

    def json_request(
        self,
        method: str,
        url: str,
        data: Any = None,
    ) -> Response | BaseResponse:
        """Make a JSON REST API request with optional Bearer token auth."""
        if self.offline_mode:
            response = self.get_page_from_file(url)
            self._prepare_json_response(url, response, data)
            return response
        headers = {
            "Accept": "application/json, text/plain, */*",
        }
        if self._bearer_token:
            headers["Authorization"] = f"Bearer {self._bearer_token}"
        kwargs: dict[str, Any] = {
            "headers": headers,
            "timeout": URL_REQUEST_TIMEOUT,
        }
        if data is not None:
            headers["Content-Type"] = "text/plain;charset=UTF-8"
            kwargs["data"] = json.dumps(data, separators=(",", ":"))
        try:
            response = requests.request(method, url, **kwargs)  # noqa: S113
        except requests.exceptions.Timeout:
            return BaseResponse()
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ChunkedEncodingError,
        ) as error:
            raise PageFetcherConnectionError from error
        self._prepare_json_response(url, response, data)
        return response

    def get_page_from_file(self, url: str) -> BaseResponse:
        """Get page from file."""
        response = BaseResponse()
        page_name = url.rsplit(sep="/", maxsplit=1)[-1] or DEFAULT_PAGE
        path = Path(f"{self.offline_path_prefix}/{page_name}")
        if path.exists():
            with path.open("r") as file:
                response.content = file.read().encode("utf-8")
                response.status_code = status_code_ok
                _LOGGER.debug(
                    "[NetgearSwitchConnector.get_page_from_file] "
                    "loaded offline page=%s",
                    page_name,
                )
        else:
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_page_from_file] offline page=%s not found",
                page_name,
            )
        return response

    def set_data_from_template(
        self, template: dict[str, Any], source: Any, data: dict[str, Any]
    ) -> None:
        """Populate data from template using class variables."""
        if "params" not in template:
            return
        for key, value in template["params"].items():
            if value.startswith("literal:"):
                data[key] = value[8:]
            else:
                try:
                    data[key] = getattr(source, value)
                except AttributeError as error:
                    message = (
                        "NetgearSwitchConnector._set_data_from_template: "
                        f"missing attribute {key} (class variable {value})"
                    )
                    raise EmptyTemplateParameterError(message) from error
                if not data[key]:
                    message = (
                        "NetgearSwitchConnector._set_data_from_template: "
                        f"empty attribute {key} (class variable {value})"
                    )
                    raise EmptyTemplateParameterError(message)

    def get_login_response(
        self,
        switch_model: type[AutodetectedSwitchModel],
        login_password: str,
        rand: str | None,
    ) -> Response | BaseResponse:
        """Login and save returned cookie."""
        if not switch_model or switch_model.MODEL_NAME == "":
            raise SwitchModelNotDetectedError
        if switch_model.CRYPT_FUNCTION == "merge_hash" and not rand:
            self._password_hash = login_password
            _LOGGER.debug(
                "[PageFetcher.get_login_response] no rand: use plaintext password"
            )
        elif switch_model.CRYPT_FUNCTION == "merge_hash" and rand:
            self._password_hash = merge_hash(login_password, rand)
            _LOGGER.debug(
                "[PageFetcher.get_login_response] use merge_hash password with rand=%s",
                rand,
            )
        elif switch_model.CRYPT_FUNCTION == "hex_hmac_md5":
            self._password_hash = hex_hmac_md5(login_password)
            _LOGGER.debug(
                "[PageFetcher.get_login_response] use hex_hmac_md5 password",
            )
        else:
            raise InvalidCryptFunctionError(switch_model.CRYPT_FUNCTION)
        response = None
        template = switch_model.LOGIN_TEMPLATE
        url = template["url"].format(ip=self.host)
        method = template["method"]
        data = {}
        self.set_data_from_template(template, self, data)
        allow_redirects = True
        response = self.request(method, url, data=data, allow_redirects=allow_redirects)
        if not response or response.status_code != status_code_ok:
            raise LoginFailedError

        return response

    def _is_authenticated(self, response: Response | BaseResponse) -> bool:
        """Check for redirect to login when not authenticated (anymore)."""
        if "content" in dir(response) and response.content:
            title = html.fromstring(response.content).xpath("//title")
            if (
                len(title)
                and title[0].text
                and title[0].text.lower() == "redirect to login"
            ):
                _LOGGER.info(
                    "[PageFetcher._is_authenticated] Returning false: title=%s",
                    title[0].text.lower(),
                )
                return False
            script = html.fromstring(response.content).xpath(
                '//script[contains(text(),"/wmi/login")]'
            )
            if (
                len(script) > 0
                and script[0].text
                and 'top.location.href = "/wmi/login"' in script[0].text
            ):
                _LOGGER.info(
                    "[PageFetcher._is_authenticated] Returning false: script=%s",
                    script[0].text,
                )
                return False
        return True

    def request(
        self,
        method: str,
        url: str,
        data: Any = None,
        timeout: int = 0,
        allow_redirects: bool = False,  # noqa: FBT001, FBT002
    ) -> Response | BaseResponse:
        """Make authenticated requests with requests.request."""
        if self.offline_mode:
            return self.get_page_from_file(url)
        if timeout == 0:
            timeout = URL_REQUEST_TIMEOUT
        response = Response()
        kwargs = {}
        data_key = "data" if method == "post" else "params"
        if self._cookie_name and self._cookie_content:
            jar = requests.cookies.RequestsCookieJar()
            if ":" in self.host:
                host_only, port_only = self.host.split(":")
                jar.set(
                    self._cookie_name,
                    self._cookie_content,
                    domain=host_only,
                    path="/",
                    port=port_only,
                )
            else:
                jar.set(
                    self._cookie_name, self._cookie_content, domain=self.host, path="/"
                )
            kwargs = {
                data_key: data,
                "cookies": jar,
                "allow_redirects": allow_redirects,
                "timeout": timeout,
            }
            _LOGGER.debug(
                "[PageFetcher.request] calling %s %s with %s cookie"
                " with %s=%s, allow_redirects=%s, timeout=%d",
                method.upper(),
                url,
                self._cookie_name,
                data_key,
                data,
                allow_redirects,
                timeout,
            )
        else:
            kwargs = {
                data_key: data,
                "allow_redirects": allow_redirects,
                "timeout": timeout,
            }
            _LOGGER.debug(
                "[PageFetcher.request] calling %s %s without cookie"
                " with %s=%s, allow_redirects=%s, timeout=%d",
                method.upper(),
                url,
                data_key,
                data,
                allow_redirects,
                timeout,
            )
        try:
            response = requests.request(method, url, **kwargs)  # noqa: S113
        except requests.exceptions.Timeout:
            return response
        except requests.exceptions.ConnectionError as error:
            raise PageFetcherConnectionError from error
        except requests.exceptions.ChunkedEncodingError as error:
            raise PageFetcherConnectionError from error

        # Session expired: refresh login cookie and try again
        if response.status_code == status_code_ok and not self._is_authenticated(
            response
        ):
            raise NotLoggedInError
        return response

    def has_ok_status(self, response: Response | BaseResponse | None) -> bool:
        """Check if response has status code 200."""
        return response is not None and response.status_code == status_code_ok
