"""HTML page retrieval classes."""

import logging
from pathlib import Path
from typing import Any

import requests
import requests.cookies
from lxml import html

from py_netgear_plus import netgear_crypt
from py_netgear_plus.models import AutodetectedSwitchModel, SwitchModelNotDetectedError

DEFAULT_PAGE = "index.htm"
URL_REQUEST_TIMEOUT = 15

_LOGGER = logging.getLogger(__name__)


class LoginFailedError(Exception):
    """Invalid credentials."""


class NotLoggedInError(Exception):
    """Not logged in."""


class PageNotLoadedError(Exception):
    """Failed to load the page."""


class BaseResponse:
    """Base class for response objects."""

    def __init__(self) -> None:
        """Initialize BaseResponse Object."""
        self.status_code = requests.codes.not_found
        self.content = b""
        self.cookies = requests.cookies.RequestsCookieJar()

    def __bool__(self) -> bool:
        """Return True if status code is 200."""
        return self.status_code == requests.codes.ok


class PageFetcher:
    """Class to fetch html pages from switch (or file)."""

    def __init__(self, host: str) -> None:
        """Initialize PageFetcher Object."""
        self.host = host
        # cached login page response
        self._login_page_response = None

        # login cookie
        self._cookie_name = None
        self._cookie_content = None

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
        url = switch_model.LOGIN_TEMPLATE["url"].format(ip=self.host)
        _LOGGER.debug("[PageFetcher.check_login_url] calling request for GET %s", url)
        self._login_page_response = self.request("get", url)
        return self.has_ok_status(self._login_page_response)

    def get_login_page_response(self) -> requests.Response | BaseResponse | None:
        """Return cached login page."""
        return self._login_page_response

    def clear_login_page_response(self) -> None:
        """Return cached login page."""
        self._login_page_response = None

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

    def get_page_from_file(self, url: str) -> BaseResponse:
        """Get page from file."""
        response = BaseResponse()
        page_name = url.split("/")[-1] or DEFAULT_PAGE
        path = Path(f"{self.offline_path_prefix}/{page_name}")
        if path.exists():
            with path.open("r") as file:
                response.content = file.read().encode("utf-8")
                response.status_code = requests.codes.ok
                _LOGGER.debug(
                    "[NetgearSwitchConnector.get_page_from_file] "
                    "loaded offline page=%s",
                    page_name,
                )
        else:
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_page_from_file] "
                "offline page=%s not found",
                page_name,
            )
        return response

    def get_login_response(
        self,
        switch_model: type[AutodetectedSwitchModel],
        login_password: str,
        rand: str | None,
    ) -> requests.Response:
        """Login and save returned cookie."""
        if not switch_model or switch_model.MODEL_NAME == "":
            raise SwitchModelNotDetectedError
        password = ""
        if not rand:
            password = login_password
        else:
            password = netgear_crypt.make_md5(netgear_crypt.merge(login_password, rand))
        response = None
        template = switch_model.LOGIN_TEMPLATE
        url = template["url"].format(ip=self.host)
        method = template["method"]
        key = template["key"]
        _LOGGER.debug(
            "[PageFetcher.get_login_page] calling request for %s %s",
            method.upper(),
            url,
        )
        response = requests.request(
            method,
            url,
            data={key: password},
            allow_redirects=True,
            timeout=URL_REQUEST_TIMEOUT,
        )
        if not response or response.status_code != requests.codes.ok:
            raise LoginFailedError

        return response

    def _is_authenticated(self, response: requests.Response | BaseResponse) -> bool:
        """Check for redirect to login when not authenticated (anymore)."""
        if "content" in dir(response) and response.content:
            title = html.fromstring(response.content).xpath("//title")
            if len(title) and title[0].text.lower() == "redirect to login":
                _LOGGER.info(
                    "[NetgearSwitchConnector._is_authenticated]"
                    " Returning false: title=%s",
                    title[0].text.lower(),
                )
                return False
            script = html.fromstring(response.content).xpath(
                '//script[contains(text(),"/wmi/login")]'
            )
            if len(script) and 'top.location.href = "/wmi/login"' in script[0].text:
                _LOGGER.info(
                    "[NetgearSwitchConnector._is_authenticated]"
                    " Returning false: script=%s",
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
    ) -> requests.Response | BaseResponse:
        """Make authenticated requests with requests.request."""
        if self.offline_mode:
            return self.get_page_from_file(url)
        if timeout == 0:
            timeout = URL_REQUEST_TIMEOUT
        jar = requests.cookies.RequestsCookieJar()
        if self._cookie_name and self._cookie_content:
            jar.set(self._cookie_name, self._cookie_content, domain=self.host, path="/")
            _LOGGER.debug(
                "[PageFetcher.request] calling %s %s with %s cookie",
                method.upper(),
                url,
                self._cookie_name,
            )
        else:
            _LOGGER.debug(
                "[PageFetcher.request] calling %s %s without cookie",
                method.upper(),
                url,
            )
        response = requests.Response()
        data_key = "data" if method == "post" else "params"
        kwargs = {
            data_key: data,
            "cookies": jar,
            "timeout": timeout,
            "allow_redirects": allow_redirects,
        }
        try:
            response = requests.request(method, url, **kwargs)  # noqa: S113
        except requests.exceptions.Timeout:
            return response
        # Session expired: refresh login cookie and try again
        if response.status_code == requests.codes.ok and not self._is_authenticated(
            response
        ):
            raise NotLoggedInError
        return response

    def has_ok_status(self, response: requests.Response | BaseResponse) -> bool:
        """Check if response has status code 200."""
        return response.status_code == requests.codes.ok
