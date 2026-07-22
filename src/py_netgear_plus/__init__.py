"""Netgear API."""

import logging
import re
import time
from contextlib import suppress
from pathlib import Path
from typing import Any

from .fetcher import (
    BaseResponse,
    LoginFailedError,
    NotLoggedInError,
    PageFetcher,
    PageFetcherConnectionError,
    PageNotLoadedError,
    Response,
    status_code_no_response,
    status_code_not_found,
    status_code_unauthorized,
)
from .models import (
    MODELS,
    AutodetectedSwitchModel,
    MultipleModelsDetectedError,
    PortNumberOutofRangeError,
    SwitchModelNotDetectedError,
    VLANMember,
)
from .parsers import NetgearPlusPageParserError, create_page_parser

__version__ = "0.6.4"

DEFAULT_PAGE = "index.htm"
MAX_AUTHENTICATION_FAILURES = 3
PORT_STATUS_CONNECTED = ["Aktiv", "Up", "UP", "CONNECTED"]
PORT_MODUS_SPEED = ["Auto"]
SWITCH_STATES = ["on", "off"]
FLOW_CONTROL = ["Enable", "Disable"]

# Port speed values used by supported Netgear Plus switch web interfaces.
PORT_SPEED_AUTO = 1
PORT_SPEED_DISABLED = 2
PORT_SPEED_10_HALF = 3
PORT_SPEED_10_FULL = 4
PORT_SPEED_100_HALF = 5
PORT_SPEED_100_FULL = 6

_LOGGER = logging.getLogger(__name__)


def _from_bytes_to_megabytes(v: float) -> float:
    bytes_to_mbytes = 1e-6
    return float(f"{round(v * bytes_to_mbytes, 2):.2f}")


def _normalize_flow_control(value: Any) -> int | None:
    """Return protocol value for flow control when it can be inferred."""
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 2
    if isinstance(value, int):
        return value if value in (1, 2) else None

    normalized = str(value).strip().lower()
    flow_control_mapping = {
        "1": 1,
        "true": 1,
        "enable": 1,
        "enabled": 1,
        "aktiv": 1,
        "2": 2,
        "false": 2,
        "disable": 2,
        "disabled": 2,
        "deaktiviert": 2,
    }
    return flow_control_mapping.get(normalized)


def _get_pending_apply_delay(response: Response | BaseResponse) -> float | None:
    """Return wait time if switch accepted a change and asks to wait."""
    if not getattr(response, "content", None):
        return None

    content = response.content
    if isinstance(content, str):
        content = content.encode("utf-8")
    if b"Please wait..." not in content:
        return None

    match = re.search(rb'http-equiv="refresh"\s+content\s*=\s*["\']?\s*(\d+)', content)
    if match:
        return float(match.group(1))
    return 4.0


class InvalidPortStatusError(Exception):
    """Number of statusses do not match number of ports."""


class InvalidSwitchStateError(Exception):
    """State should be one of the options in SWITCH_STATES."""


class InvalidPoEPortError(Exception):
    """Port is not a PoE port."""


class PortNotVLANMemberError(Exception):
    """Port is not a member of a VLAN."""


def _normalize_ports(ports_config: str | list) -> str:
    """Coerce a list-of-strings ports_config to its single-char form."""
    if isinstance(ports_config, list):
        return "".join(x[0] for x in ports_config)
    return ports_config


def _cfg_to_ports_string(cfg: dict[int, "VLANMember"]) -> str:
    """Render a port→VLANMember mapping as a 'TUUUUUUE' string."""
    return "".join(cfg[port] for port in sorted(cfg))


def _record(
    summary: dict[str, list],
    ok: bool,  # noqa: FBT001
    bucket: str,
    item: Any,
    op: str,
) -> None:
    """Append item to bucket on success or to the 'failed' bucket otherwise."""
    if ok:
        summary[bucket].append(item)
    else:
        summary["failed"].append((op, item))


class NetgearSwitchConnector:
    """Representation of a Netgear Switch."""

    # The switch goes briefly unresponsive during state transitions
    # (VLAN mode flip, IP/DHCP change) and during transient timeouts.
    # These sleeps give it time to settle so the next request lands on
    # the committed state.
    VLAN_MODE_SETTLE_SECONDS = 3.0
    IP_CONFIG_SETTLE_SECONDS = 3.0
    RETRY_BACKOFF_SECONDS = 3.0

    def __init__(self, host: str, password: str) -> None:
        """Initialize Connector Object."""
        self.host = host

        # initial values
        self.switch_model = AutodetectedSwitchModel
        self._page_fetcher = PageFetcher(host)
        self._page_parser = create_page_parser()
        self.ports = 0
        self.poe_ports = []
        self._switch_bootloader = "unknown"

        # sleep time between requests
        self.sleep_time = 0.25

        # Login related instance variables
        # plain login password
        self._password = password
        # Model page template param variables
        self._client_hash = None
        self._gambit = None

        self._authentication_failure_count = 0

        # previous data calculation
        self._previous_timestamp = time.perf_counter()
        self._previous_data = {}

        # current data
        self._loaded_switch_metadata = {}

        _LOGGER.debug(
            "[NetgearSwitchConnector] instance (v%s) created for IP=%s",
            __version__,
            self.host,
        )
        _LOGGER.debug(
            "[NetgearSwitchConnector] DEBUG logging enabled. "
            "Your logs may contain sensitve information like "
            "passwords or session cookies. Do not use in production."
        )

    def turn_on_offline_mode(self, path_prefix: str) -> None:
        """Turn on offline mode."""
        self._page_fetcher.turn_on_offline_mode(path_prefix)

    def turn_on_online_mode(self) -> None:
        """Turn on online mode."""
        self._page_fetcher.turn_on_online_mode()

    def get_offline_mode(self) -> bool:
        """Get offline mode status."""
        return self._page_fetcher.offline_mode

    @property
    def _is_json_api(self) -> bool:
        """Return True if switch uses JSON REST API."""
        return getattr(self.switch_model, "API_TYPE", "") == "json_rest"

    def _json_api_login(self) -> bool:
        """Login via JSON REST API (MS-series switches)."""
        login_template = self.switch_model.LOGIN_TEMPLATE
        login_url = login_template["url"].format(ip=self.host)
        login_method = login_template["method"]
        session_template = self.switch_model.LOGIN_SESSION_TEMPLATE
        session_url = session_template["url"].format(ip=self.host)
        session_method = session_template["method"]
        try:
            response = self._page_fetcher.json_request(
                login_method,
                login_url,
                data={"password": self._password},
            )
            if not self._page_fetcher.has_ok_status(response):
                return False
            data = response.json()
            if data.get("errCode") != 0:
                return False
            token = data.get("token")
            session_id = data.get("id")
            if not token or not session_id:
                return False
            self._page_fetcher.set_bearer_token(token)
            response2 = self._page_fetcher.json_request(
                session_method,
                session_url,
                data={"id": session_id, "status": True},
            )
            if not self._page_fetcher.has_ok_status(response2):
                self._page_fetcher.clear_bearer_token()
                return False
        except (PageFetcherConnectionError, ValueError, KeyError):
            return False
        _LOGGER.info(
            "[NetgearSwitchConnector._json_api_login] "
            "JSON REST API login successful for IP=%s",
            self.host,
        )
        return True

    def _json_api_fetch(self, templates: list) -> Response | BaseResponse:
        """Fetch a JSON REST API endpoint with retry on auth failure."""
        for template in templates:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            response = self._page_fetcher.json_request(method, url)
            if (
                response.status_code == status_code_unauthorized
                and self._json_api_login()
            ):
                response = self._page_fetcher.json_request(method, url)
            if self._page_fetcher.has_ok_status(response):
                return response
        message = f"Failed to load any JSON API endpoint: {templates}"
        raise PageNotLoadedError(message)

    def _autodetect_json_api(self) -> type[AutodetectedSwitchModel] | None:
        """Try to detect switch model via JSON REST API."""
        json_api_models = [
            m for m in MODELS if getattr(m, "API_TYPE", "") == "json_rest"
        ]
        for mdl_cls in json_api_models:
            mdl = mdl_cls()
            # Temporarily set model so login templates are available
            self._set_instance_attributes_by_model(mdl)
            with suppress(PageFetcherConnectionError, PageNotLoadedError):
                response = self._json_api_fetch(mdl.AUTODETECT_TEMPLATES)
                try:
                    data = response.json()
                    model_number = data.get("systemInfo", {}).get("modelNumber", "")
                    if model_number == mdl.MODEL_NAME:
                        self._page_parser = create_page_parser(
                            self.switch_model.MODEL_NAME
                        )
                        return self.switch_model
                except (ValueError, KeyError):
                    pass
        self.switch_model = AutodetectedSwitchModel
        return None

    def autodetect_model(self) -> type[AutodetectedSwitchModel]:
        """Detect switch model from login page contents."""
        _LOGGER.debug(
            "[NetgearSwitchConnector.autodetect_model] called for IP=%s", self.host
        )
        # Try JSON REST API detection (MS-series switches)
        json_api_model = self._autodetect_json_api()
        if json_api_model:
            _LOGGER.info(
                "[NetgearSwitchConnector.autodetect_model] "
                "found %s switch via JSON REST API.",
                json_api_model.MODEL_NAME,
            )
            return json_api_model

        for template in AutodetectedSwitchModel.AUTODETECT_TEMPLATES:
            response = None
            url = template["url"].format(ip=self.host)
            method = template["method"]
            with suppress(PageFetcherConnectionError):
                response = self._page_fetcher.request(
                    method,
                    url,
                )

            if response and self._page_fetcher.has_ok_status(response):
                passed_checks_by_model = {}
                matched_models = []
                for mdl_cls in MODELS:
                    mdl = mdl_cls()
                    if getattr(mdl, "API_TYPE", "") == "json_rest":
                        continue
                    mdl_name = mdl.MODEL_NAME
                    passed_checks_by_model[mdl_name] = {}
                    autodetect_funcs = mdl.get_autodetect_funcs()
                    for func_name, expected_results in autodetect_funcs:
                        func_result = getattr(self._page_parser, func_name)(response)
                        check_successful = func_result in expected_results
                        passed_checks_by_model[mdl_name][func_name] = check_successful

                        # check_login_switchinfo_tag beats them all
                        if (
                            func_name == "check_login_switchinfo_tag"
                            and check_successful
                        ):
                            matched_models.append(mdl)

                    values_for_current_mdl = passed_checks_by_model[mdl_name].values()
                    if all(values_for_current_mdl) and mdl not in matched_models:
                        matched_models.append(mdl)

                if len(matched_models) == 1:
                    # set local settings
                    self._set_instance_attributes_by_model(matched_models[0])
                    _LOGGER.info(
                        "[NetgearSwitchConnector.autodetect_model] found %s switch.",
                        matched_models[0].MODEL_NAME,
                    )
                    if self.switch_model:
                        self._page_parser = create_page_parser(
                            self.switch_model.MODEL_NAME
                        )
                        return self.switch_model
                if len(matched_models) > 1:
                    raise MultipleModelsDetectedError(str(matched_models))
                _LOGGER.debug(
                    "[NetgearSwitchConnector.autodetect_model] "
                    "passed_checks_by_model=%s matched_models=%s",
                    passed_checks_by_model,
                    matched_models,
                )
        raise SwitchModelNotDetectedError

    def _set_instance_attributes_by_model(
        self, switch_model: type[AutodetectedSwitchModel]
    ) -> None:
        self.switch_model = switch_model
        self.ports = switch_model.PORTS
        self.poe_ports = switch_model.POE_PORTS
        self._previous_data = {
            "traffic_tx": [0] * self.ports,
            "traffic_rx": [0] * self.ports,
            "crc_errors": [0] * self.ports,
            "speed_io": [0] * self.ports,
            "sum_rx": [0] * self.ports,
            "sum_tx": [0] * self.ports,
        }

    def get_unique_id(self) -> str:
        """Return unique identifier from switch model and ip address."""
        if self.switch_model.MODEL_NAME == "":
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_unique_id] switch_model is None, "
                "try NetgearSwitchConnector.autodetect_model"
            )
            self.autodetect_model()
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_unique_id] now switch_model is %s",
                str(self.switch_model),
            )
        model_lower = self.switch_model.MODEL_NAME.lower()
        return model_lower + "_" + self.host.replace(".", "_")

    def _handle_soft_authentication_failure(
        self, response: Response | BaseResponse
    ) -> None:
        """Handle soft authentication failure."""
        # Clear cached login data
        self._page_fetcher.clear_login_page_response()

        if "content" not in dir(response):
            message = "No content in login form response."
            raise LoginFailedError(message)

        # Handling Error Messages
        error_msg = self._page_parser.parse_error(response)
        if error_msg:
            _LOGGER.warning(
                "[NetgearSwitchConnector.handle_soft_authentication_failure]"
                ' [IP: %s] Response from switch: "%s"',
                self.host,
                error_msg,
            )
        else:
            _LOGGER.debug(
                "[NetgearSwitchConnector.handle_soft_authentication_failure]"
                " No error message found in response:\n\n%s",
                response.content.decode("utf-8"),
            )

        self._authentication_failure_count += 1
        if self._authentication_failure_count >= MAX_AUTHENTICATION_FAILURES:
            count = self._authentication_failure_count
            message = f"Too many authentication failures ({count})."
            raise LoginFailedError(message)

    def get_login_cookie(self) -> bool:
        """Login and save returned cookie."""
        if not self.switch_model or self.switch_model.MODEL_NAME == "":
            self.autodetect_model()
        if self._is_json_api:
            if self._page_fetcher.has_bearer_token():
                return True
            return self._json_api_login()
        if not self._page_fetcher.get_login_page_response():
            self._page_fetcher.check_login_url(self.switch_model)
        rand = self._page_parser.parse_login_form_rand(
            self._page_fetcher.get_login_page_response()
        )

        response = self._page_fetcher.get_login_response(
            self.switch_model, self._password, rand
        )

        _LOGGER.debug(
            "[NetgearSwitchConnector.get_login_cookie] looking for cookies: %s",
            ", ".join(self.switch_model.ALLOWED_COOKIE_TYPES),
        )
        # GS31xEP(P) series switches return the cookie value in a hidden form element
        self._gambit = self._page_parser.parse_gambit_tag(response)
        if self._gambit:
            self._page_fetcher.set_cookie(
                self.switch_model.ALLOWED_COOKIE_TYPES[0], self._gambit
            )
            _LOGGER.debug("[NetgearSwitchConnector.get_login_cookie] Found Gambit tag:")
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_login_cookie] Setting cookie %s=%s",
                self.switch_model.ALLOWED_COOKIE_TYPES[0],
                str(self._gambit),
            )
            self._authentication_failure_count = 0
            return True
        # Other switches return a cookie on successful login
        for ct in self.switch_model.ALLOWED_COOKIE_TYPES:
            cookie = response.cookies.get(ct, None)
            if cookie:
                _LOGGER.debug(
                    "[NetgearSwitchConnector.get_login_cookie] Found cookie %s", ct
                )
                self._page_fetcher.set_cookie(ct, cookie)
                self._authentication_failure_count = 0
                return True
        _LOGGER.debug(
            "[NetgearSwitchConnector.get_login_cookie] "
            "No Gambit tag or valid cookie found."
        )
        self._handle_soft_authentication_failure(response)
        return False

    def get_cookie(self) -> tuple[str | None, str | None]:
        """Return cookie."""
        return self._page_fetcher.get_cookie()

    def set_cookie(self, name: str, content: str) -> None:
        """Return cookie."""
        if name == "gambitCookie":
            self._gambit = content
        return self._page_fetcher.set_cookie(name, content)

    def _validate_switch_port_request(self, port: int, state: str) -> None:
        """Validate switch_port inputs and model capabilities."""
        if not self.switch_model.MODEL_NAME:
            self.autodetect_model()
        if state not in SWITCH_STATES:
            message = f'State "{state}" not in {SWITCH_STATES}.'
            raise InvalidSwitchStateError(message)
        if not self.switch_model.SWITCH_PORT_TEMPLATES:
            message = "No switch port templates found."
            raise NotImplementedError(message)
        if port < 1 or port > self.ports:
            message = f"Port {port} not in range 1-{self.ports}."
            raise PortNumberOutofRangeError(message)

    def _request_switch_port_change(
        self, method: str, url: str, data: dict[str, Any]
    ) -> Response | BaseResponse:
        """Send a switch_port request, retrying once after login refresh."""
        try:
            return self._page_fetcher.request(method, url, data)
        except NotLoggedInError as error:
            if self.get_login_cookie():
                return self._page_fetcher.request(method, url, data)
            message = "Not logged in and unable to login."
            raise LoginFailedError(message) from error

    def delete_login_cookie(self) -> bool:
        """Logout and delete cookie."""
        """Only used while testing. Prevents "Maximum number of sessions" error."""
        if not self.switch_model or self.switch_model.MODEL_NAME == "":
            self.autodetect_model()
        if self._is_json_api:
            self._page_fetcher.clear_bearer_token()
            return True
        response = BaseResponse()
        for template in self.switch_model.LOGOUT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = {}
            self._page_fetcher.set_data_from_template(template, self, data)

            if not self.get_offline_mode():
                try:
                    response = self._page_fetcher.request(method, url, data)
                    break  # Exit the loop if the request is successful
                except NotLoggedInError:
                    response.status_code = status_code_unauthorized
                    response.content = b""
                    break
                except PageFetcherConnectionError:
                    _LOGGER.debug(
                        "NetgearSwitchConnector.fetch_page: "
                        "caught PageFetcherConnectionError"
                    )
                    response.status_code = status_code_no_response
                    response.content = b""
                    break  # Stop retrying after a connection error
            else:
                response = self._page_fetcher.get_page_from_file(url)

            if response.status_code != status_code_not_found:
                break

        _LOGGER.debug(
            "[NetgearSwitchConnector.delete_login_cookie] "
            "logout response status code=%s",
            response.status_code,
        )
        self._page_fetcher.clear_cookie()
        return response.status_code != status_code_not_found

    def reboot(self) -> bool:
        """Reboot the switch."""
        if not self.switch_model.has_reboot_button():
            _LOGGER.info("[NetgearSwitchConnector.reboot] Reboot button not available.")
            return False

        response = BaseResponse()
        for template in self.switch_model.SWITCH_REBOOT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = {}
            if not self.get_offline_mode():
                self._page_fetcher.set_data_from_template(template, self, data)
            response = self.fetch_page(method, url, data)
            if self._page_parser.parse_reboot_success(response):
                return True

        _LOGGER.debug(
            "[NetgearSwitchConnector.reboot] failed to load any page of templates: %s",
            self.switch_model.SWITCH_REBOOT_TEMPLATES,
        )
        return False

    def vlan_status(self) -> dict:
        """Get informations about current vlan mode, and its configuration."""
        if not self.switch_model.VLAN_STATUS_TEMPLATES:
            message = "VLAN status cannot be queried on this model"
            raise NotImplementedError(message)
        response = self.fetch_page_from_templates(
            self.switch_model.VLAN_STATUS_TEMPLATES
        )
        return self._page_parser.parse_vlan_status(response)

    def set_vlan_mode(self, mode: str) -> bool:
        """Set vlan mode."""
        if not self.switch_model.VLAN_MODE_SET_TEMPLATES:
            message = "VLAN mode cannot be changed on this model"
            raise NotImplementedError(message)

        for template in self.switch_model.VLAN_MODE_SET_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_vlan_mode_data(mode)  # type: ignore[report-call-issue]
            _LOGGER.debug("vlan_mode data=%s", data)
            self._page_fetcher.set_data_from_template(template, self, data)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            if self._page_fetcher.has_ok_status(response):
                # Clear cached metadata to refetch on next poll
                self._loaded_switch_metadata = {}
                # Switch becomes unresponsive for a few seconds after a
                # mode change; let it settle before the caller fires
                # the next request.
                time.sleep(self.VLAN_MODE_SETTLE_SECONDS)
                return True
            content = response.content
            if isinstance(content, (bytes, str)):
                content = content.strip()
            _LOGGER.warning(
                "NetgearSwitchConnector.set_vlan_mode response was %s",
                content,
            )
        return False

    def add_vlan(
        self,
        vlan_id: int,
        vlan_name: str | None = None,
        ports_config: str | list | None = None,
        voice_vlan: bool = False,  # noqa: FBT001, FBT002
        voice_cos: int = 6,
    ) -> bool:
        """Add a new VLAN."""
        return self._set_advanced_vlan_parameter(
            "Add", vlan_id, vlan_name, ports_config, voice_vlan, voice_cos
        )

    def edit_vlan(
        self,
        vlan_id: int,
        vlan_name: str | None = None,
        ports_config: str | list | None = None,
        voice_vlan: bool = False,  # noqa: FBT001, FBT002
        voice_cos: int = 6,
    ) -> bool:
        """Edit an existing VLAN."""
        return self._set_advanced_vlan_parameter(
            "Apply", vlan_id, vlan_name, ports_config, voice_vlan, voice_cos
        )

    def remove_vlan(self, vlan_id: int) -> bool:
        """Remove a VLAN."""
        return self._set_advanced_vlan_parameter("Delete", vlan_id)

    def _set_advanced_vlan_parameter(  # noqa: PLR0913
        self,
        action: str,
        vlan_id: int,
        vlan_name: str | None = None,
        ports_config: str | list | None = None,
        voice_vlan: bool = False,  # noqa: FBT001, FBT002
        voice_cos: int = 6,
    ) -> bool:
        """Change advanced vlan parameters."""
        if not self.switch_model.VLAN_ADVANCED_SET_TEMPLATES:
            message = "VLAN advanced parameters cannot be changed on this model"
            raise NotImplementedError(message)

        for template in self.switch_model.VLAN_ADVANCED_SET_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]

            data = self.switch_model.get_advanced_vlan_data(
                action, vlan_id, vlan_name, ports_config, voice_vlan, voice_cos
            )  # type: ignore[report-call-issue]
            _LOGGER.debug("advanced_vlan_parameter data=%s", data)
            self._page_fetcher.set_data_from_template(template, self, data)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            # It doesn't look like there is any way to know that the action failed.
            # For example, deleting a VLAN that do not exist return 200 with no
            # error or warn in sight.
            if self._page_fetcher.has_ok_status(response):
                # Clear cached metadata to refetch on next poll
                self._loaded_switch_metadata = {}
                return True
            content = response.content
            if isinstance(content, (bytes, str)):
                content = content.strip()
            _LOGGER.warning(
                "NetgearSwitchConnector.set_advanced_vlan_parameter response was %s",
                content,
            )
        return False

    def set_vlan_pvid(self, port_idx: int, vlan_id: int) -> bool:
        """Set pvid for a vlan."""
        if not self.switch_model.VLAN_PVID_SET_TEMPLATES:
            message = "VLAN pvid parameters cannot be changed on this model"
            raise NotImplementedError(message)

        for template in self.switch_model.VLAN_PVID_SET_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]

            data = self.switch_model.get_pvid_data(port_idx, vlan_id)  # type: ignore[report-call-issue]
            _LOGGER.debug("vlan_pvid data=%s", data)
            self._page_fetcher.set_data_from_template(template, self, data)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            if self._page_fetcher.has_ok_status(response):
                # It does not seem there is anything to latch on except
                # checking if the message size is to small to be an
                # HTML answer.
                content_min_size = 30
                if len(response.content) < content_min_size:
                    raw = response.content
                    if isinstance(raw, bytes):
                        raw = raw.decode(errors="replace")
                    r = raw.split("@")
                    min_parts = 3
                    if len(r) >= min_parts:
                        message = f"Port {r[1]} is not a member of VLAN {r[2][1:-1]}"
                    else:
                        message = f"Unexpected short response: {raw!r}"
                    raise PortNotVLANMemberError(message)
                # Clear cached metadata to refetch on next poll
                self._loaded_switch_metadata = {}
                return True
            content = response.content
            if isinstance(content, (bytes, str)):
                content = content.strip()
            _LOGGER.warning(
                "NetgearSwitchConnector.set_vlan_pvid response was %s",
                content,
            )
        return False

    def get_port_settings(self) -> dict[int, dict[str, Any]]:
        """Return per-port settings (name/speed/rates/flow-control)."""
        if not self.switch_model.PORT_SETTINGS_TEMPLATES:
            message = "Port settings cannot be read on this model"
            raise NotImplementedError(message)
        response = self.fetch_page_from_templates(
            self.switch_model.SWITCH_INFO_TEMPLATES
        )
        return self._page_parser.parse_port_settings(response)

    def set_port_settings(  # noqa: PLR0913
        self,
        port: int,
        *,
        name: str | None = None,
        speed: int | None = None,
        flow_control: int | bool | str | None = None,
        ingress_rate: int | None = None,
        egress_rate: int | None = None,
    ) -> bool:
        """Update selected settings for a port, preserving unspecified values."""
        if not self.switch_model.PORT_SETTINGS_TEMPLATES:
            message = "Port settings cannot be changed on this model"
            raise NotImplementedError(message)

        all_settings = self.get_port_settings()
        if port not in all_settings:
            message = f"Port {port} not found on switch"
            raise PortNumberOutofRangeError(message)
        current = all_settings[port]

        selected_flow_control = (
            current["flow_control"] if flow_control is None else flow_control
        )
        normalized_flow_control = _normalize_flow_control(selected_flow_control)
        if normalized_flow_control is None:
            message = f"Invalid flow control value: {selected_flow_control!r}"
            raise ValueError(message)

        # The POST template requires a client hash. Load it automatically so
        # callers can write settings immediately after logging in.
        if not self._client_hash:
            self._get_switch_metadata()

        for template in self.switch_model.PORT_SETTINGS_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_port_settings_data(
                port=port,
                description=current["name"] if name is None else name,
                speed=current["speed"] if speed is None else speed,
                flow_control=normalized_flow_control,
                ingress_rate=(
                    current["ingress_rate"]
                    if ingress_rate is None
                    else ingress_rate
                ),
                egress_rate=(
                    current["egress_rate"]
                    if egress_rate is None
                    else egress_rate
                ),
                priority=0,
            )
            _LOGGER.debug("set_port_settings data=%s", data)
            self._page_fetcher.set_data_from_template(template, self, data)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            if self._page_fetcher.has_ok_status(response):
                self._loaded_switch_metadata = {}
                return True
            content = response.content
            if isinstance(content, (bytes, str)):
                content = content.strip()
            _LOGGER.warning(
                "NetgearSwitchConnector.set_port_settings response was %s", content
            )
        return False

    def set_port_name(self, port: int, name: str) -> bool:
        """Rename a port, preserving other port settings."""
        return self.set_port_settings(port, name=name)

    def get_ip_config(self) -> dict[str, Any]:
        """Return current IP/DHCP configuration."""
        if not self.switch_model.IP_CONFIG_TEMPLATES:
            message = "IP config cannot be read on this model"
            raise NotImplementedError(message)
        response = self.fetch_page_from_templates(self.switch_model.IP_CONFIG_TEMPLATES)
        return self._page_parser.parse_ip_config(response)

    def set_ip_config(
        self,
        *,
        dhcp: bool,
        ip_address: str = "",
        subnet_mask: str = "",
        gateway: str = "",
    ) -> bool:
        """
        Set IP/DHCP configuration.

        Setting dhcp=True ignores ip_address/subnet_mask/gateway.
        For static mode all three address fields are required.

        Caveat: when the new configuration changes the switch's IP
        (static->different IP, static->DHCP yielding a different lease,
        or DHCP->static), the switch tears down the current TCP
        connection before the HTTP response is sent. This method then
        returns False and logs an empty response, even though the
        change was applied. To confirm, ping the new address and call
        get_ip_config() against it.
        """
        if not self.switch_model.IP_CONFIG_SET_TEMPLATES:
            message = "IP config cannot be set on this model"
            raise NotImplementedError(message)
        if not dhcp and not (ip_address and subnet_mask and gateway):
            message = "Static mode requires ip_address, subnet_mask and gateway"
            raise ValueError(message)

        for template in self.switch_model.IP_CONFIG_SET_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_ip_config_data(
                dhcp=dhcp,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                gateway=gateway,
            )
            _LOGGER.debug("set_ip_config data=%s", data)
            self._page_fetcher.set_data_from_template(template, self, data)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            if self._page_fetcher.has_ok_status(response):
                self._loaded_switch_metadata = {}
                # The switch applies the new addressing asynchronously;
                # a get_ip_config() fired immediately will still report
                # the old state.
                time.sleep(self.IP_CONFIG_SETTLE_SECONDS)
                return True
            content = response.content
            if isinstance(content, (bytes, str)):
                content = content.strip()
            _LOGGER.warning(
                "NetgearSwitchConnector.set_ip_config response was %s", content
            )
        return False

    def _ensure_password_change_hash(self) -> None:
        """
        Populate self._client_hash via dashboard or factory fallback.

        Raises RuntimeError if no hash can be obtained from either path.
        Always re-fetches: a hash cached from an earlier request may
        already be stale on the switch (change_password.cgi answers
        "CHECK HASH FAILED" in that case).
        """
        self._client_hash = None
        self._loaded_switch_metadata = {}
        with suppress(NetgearPlusPageParserError, PageNotLoadedError):
            self._get_switch_metadata()
        if self._client_hash:
            return
        if self.switch_model.INITIAL_PASSWORD_HASH_TEMPLATES:
            try:
                page = self.fetch_page_from_templates(
                    self.switch_model.INITIAL_PASSWORD_HASH_TEMPLATES
                )
            except PageNotLoadedError:
                page = None
            if page is not None:
                with suppress(NetgearPlusPageParserError):
                    self._client_hash = self._page_parser.parse_initial_password_hash(
                        page
                    )
        if not self._client_hash:
            message = (
                "Could not obtain client hash for password change "
                "(neither dashboard nor factory fallback yielded one)."
            )
            raise RuntimeError(message)

    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the admin password.

        On success the switch invalidates the current session; this
        method updates the connector's stored password so the next call
        triggers an automatic re-login with the new password.

        Works both on a normally configured switch (hash read from
        dashboard.cgi) and on a factory-state switch (hash read from
        the changeDefPwdCk.cgi iframe shown on /index.cgi).
        """
        if not self.switch_model.PASSWORD_CHANGE_TEMPLATES:
            message = "Password change is not supported on this model"
            raise NotImplementedError(message)

        self._ensure_password_change_hash()

        for template in self.switch_model.PASSWORD_CHANGE_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_password_change_data(
                old_password, new_password
            )
            self._page_fetcher.set_data_from_template(template, self, data)
            headers = self._resolve_template_headers(template)

            response = BaseResponse
            try:
                response = self._page_fetcher.request(
                    method, url, data, headers=headers
                )
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(
                        method, url, data, headers=headers
                    )
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error

            body = response.content
            if isinstance(body, bytes):
                body = body.decode(errors="replace")
            body_stripped = (body or "").strip()
            if (
                self._page_fetcher.has_ok_status(response)
                and body_stripped == "SUCCESS"
            ):
                self._password = new_password
                self._client_hash = None
                self._loaded_switch_metadata = {}
                return True
            if body_stripped == "INCORRECT":
                message = "Old password is incorrect"
                raise LoginFailedError(message)
            _LOGGER.warning(
                "NetgearSwitchConnector.change_password response was %s",
                body_stripped,
            )
        return False

    def _diff_desired_vlans(
        self,
        desired_vlans: dict,
        current_vlans: dict,
        summary: dict[str, list],
    ) -> list[tuple]:
        """Issue add_vlan calls and return list of pending edits."""
        edits_pending: list[tuple] = []
        for vlan_id, spec in desired_vlans.items():
            name = spec.get("name")
            ports_config = _normalize_ports(spec["ports_config"])
            voice_vlan = bool(spec.get("voice_vlan", False))
            voice_cos = int(spec.get("voice_cos", 6))

            if vlan_id not in current_vlans:
                ok = self.add_vlan(vlan_id, name, ports_config, voice_vlan, voice_cos)
                _record(summary, ok, "added", vlan_id, "add")
                continue

            cur = current_vlans[vlan_id]
            cur_ports = _cfg_to_ports_string(cur["cfg"])
            if cur.get("name") != name or cur_ports != ports_config:
                edits_pending.append(
                    (vlan_id, name, ports_config, voice_vlan, voice_cos)
                )
            else:
                summary["skipped"].append(vlan_id)
        return edits_pending

    def _apply_pvids(
        self,
        desired_pvids: dict,
        current_ports: dict,
        summary: dict[str, list],
    ) -> None:
        for port, vlan_id in desired_pvids.items():
            current_pvid = current_ports.get(port, {}).get("pvid")
            if current_pvid == vlan_id:
                continue
            ok = self.set_vlan_pvid(port, vlan_id)
            _record(summary, ok, "pvids_set", (port, vlan_id), "pvid")

    def _strict_remove(
        self,
        desired_vlans: dict,
        current_vlans: dict,
        summary: dict[str, list],
    ) -> None:
        for vlan_id in list(current_vlans):
            if vlan_id in desired_vlans:
                continue
            if vlan_id == 1 and 1 not in desired_vlans:
                summary["skipped"].append(vlan_id)
                continue
            ok = self.remove_vlan(vlan_id)
            _record(summary, ok, "removed", vlan_id, "remove")

    def apply_vlan_config(
        self,
        config: dict,
        *,
        strict: bool = False,
    ) -> dict:
        """
        Reconcile switch VLAN state against a desired config.

        Expected keys:
            mode (str): required, e.g. "adv8021Q"
            vlans (dict[int, dict]): id -> {name, ports_config,
                voice_vlan?, voice_cos?}
            pvids (dict[int, int]): port -> vlan_id

        strict=True removes VLANs not listed (except VLAN 1 unless
        the user lists it).

        Operation order is add → pvid → edit → remove to avoid a
        switch quirk that silently drops an edit excluding a port
        whose PVID still points to that VLAN.
        """
        desired_mode = config.get("mode")
        if not desired_mode:
            message = "config['mode'] is required"
            raise ValueError(message)

        desired_vlans = config.get("vlans") or {}
        desired_pvids = config.get("pvids") or {}

        current = self.vlan_status()
        if current.get("mode") != desired_mode:
            if not self.set_vlan_mode(desired_mode):
                message = f"Failed to set VLAN mode to {desired_mode!r}"
                raise RuntimeError(message)
            current = self.vlan_status()
        current_vlans = current.get("vlans") or {}
        current_ports = current.get("ports") or {}

        summary: dict[str, list] = {
            "added": [],
            "edited": [],
            "removed": [],
            "pvids_set": [],
            "skipped": [],
            "failed": [],
        }

        edits_pending = self._diff_desired_vlans(desired_vlans, current_vlans, summary)
        self._apply_pvids(desired_pvids, current_ports, summary)
        for vlan_id, name, ports_config, voice_vlan, voice_cos in edits_pending:
            ok = self.edit_vlan(vlan_id, name, ports_config, voice_vlan, voice_cos)
            _record(summary, ok, "edited", vlan_id, "edit")
        if strict:
            self._strict_remove(desired_vlans, current_vlans, summary)

        return summary

    def fetch_page(
        self,
        method: str,
        url: str,
        data: dict,
        headers: dict[str, str] | None = None,
    ) -> Response | BaseResponse:
        """Fetch url and retry when first response is a redirect to the login page."""
        response = BaseResponse()
        if not self.get_offline_mode():
            for attempt in range(2):
                try:
                    response = self._page_fetcher.request(
                        method, url, data, headers=headers
                    )
                    break  # Exit the loop if the request is successful
                except NotLoggedInError as error:
                    if attempt == 0 and self.get_login_cookie():
                        continue  # Retry the request if login cookie is available
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error
                except PageFetcherConnectionError:
                    _LOGGER.debug(
                        "NetgearSwitchConnector.fetch_page: "
                        "caught PageFetcherConnectionError"
                    )
                    response.status_code = status_code_no_response
                    response.content = b""
                    break  # Stop retrying after a connection error
        else:
            response = self._page_fetcher.get_page_from_file(url)
        return response

    def fetch_page_from_templates(self, templates: list) -> Response | BaseResponse:
        """
        Return response for 1st successful request from templates.

        Retries once if every template fails. A timeout-shaped failure
        (no status_code, empty body) gets a short backoff and a plain
        re-fetch (no re-login). A non-timeout failure attempts
        ``get_login_cookie`` first in case the SID was invalidated.
        """

        def attempt() -> Response | BaseResponse:
            last: Response | BaseResponse = BaseResponse()
            for template in templates:
                url = template["url"].format(ip=self.host)
                method = template["method"]
                data: dict = {}
                if not self.get_offline_mode():
                    self._page_fetcher.set_data_from_template(template, self, data)
                headers = self._resolve_template_headers(template)
                last = self.fetch_page(method, url, data, headers=headers)
                if self._page_fetcher.has_ok_status(last):
                    return last
            return last

        result = attempt()
        if self._page_fetcher.has_ok_status(result):
            return result

        looks_like_timeout = getattr(
            result, "status_code", None
        ) is None and not getattr(result, "content", None)
        if self.get_offline_mode():
            pass
        elif looks_like_timeout:
            time.sleep(self.RETRY_BACKOFF_SECONDS)
            result = attempt()
        elif self.get_login_cookie():
            result = attempt()
        if self._page_fetcher.has_ok_status(result):
            return result

        message = f"Failed to load any page of templates: {templates}"
        raise PageNotLoadedError(message)

    def _resolve_template_headers(self, template: dict) -> dict[str, str] | None:
        """Format header values with {ip} so templates can carry e.g. Referer."""
        headers = template.get("headers")
        if not headers:
            return None
        return {k: v.format(ip=self.host) for k, v in headers.items()}

    def get_switch_infos(self) -> dict[str, Any]:
        """Return dict with all available statistics."""
        if not self.switch_model.MODEL_NAME:
            self.autodetect_model()

        current_data = {}
        switch_data = {}

        if not self._loaded_switch_metadata:
            self._get_switch_metadata()
        switch_data.update(**self._loaded_switch_metadata)

        # Fetch Port Status
        time.sleep(self.sleep_time)
        switch_data.update(self._get_port_status())

        # Hold fire
        time.sleep(self.sleep_time)

        _start_time = time.perf_counter()

        current_data = self._initialize_current_data()
        # Parse port statistics html
        current_data.update(self._get_port_statistics())

        if not self.get_offline_mode():
            sample_time = _start_time - self._previous_timestamp
        else:
            sample_time = 0
        switch_data["response_time_s"] = round(sample_time, 1)

        self._update_current_data(current_data, switch_data, sample_time)

        switch_data.update(self._updated_switch_data(current_data))

        # Partially supported models fail parsing below this line
        if not self.switch_model.SUPPORTED:
            return switch_data

        if len(self.switch_model.POE_PORTS):
            time.sleep(self.sleep_time)
            switch_data.update(self._get_poe_port_config())
            time.sleep(self.sleep_time)
            switch_data.update(self._get_poe_port_status())

        # set previous data
        self._previous_timestamp = time.perf_counter()
        self._previous_data = current_data

        return switch_data

    def _get_switch_metadata(self) -> None:
        if not self.switch_model:
            self.autodetect_model()
        if self._is_json_api:
            page = self._json_api_fetch(self.switch_model.SWITCH_INFO_TEMPLATES)
        else:
            page = self.fetch_page_from_templates(
                self.switch_model.SWITCH_INFO_TEMPLATES
            )
        if not page.content:
            return
        switch_metadata = {"switch_ip": self.host}
        if not self._is_json_api:
            self._client_hash = self._page_parser.parse_client_hash(page)
            if self.switch_model.SWITCH_LED_TEMPLATES:
                switch_metadata.update(self._page_parser.parse_led_status(page))

        # Avoid a second call on next get_switch_infos() call
        self._loaded_switch_metadata = (
            switch_metadata | self._page_parser.parse_switch_metadata(page)
        )

    def _get_port_statistics(self) -> dict[str, Any]:
        if self._is_json_api:
            response = self._json_api_fetch(self.switch_model.PORT_STATISTICS_TEMPLATES)
        else:
            response = self.fetch_page_from_templates(
                self.switch_model.PORT_STATISTICS_TEMPLATES
            )
        return self._page_parser.parse_port_statistics(response, self.ports)

    def _initialize_current_data(self) -> dict:
        """Initialize current data dictionary with default values."""
        current_data = {}
        for key in [
            "sum_port_traffic_rx",
            "sum_port_traffic_tx",
            "sum_port_crc_errors",
            "sum_port_speed_rx",
            "sum_port_speed_tx",
        ]:
            current_data[key] = 0
        return current_data

    def _update_current_data(
        self, current_data: dict, switch_data: dict, sample_time: float
    ) -> None:
        """Update current data with calculated values."""
        sample_factor = 1 if not sample_time else 1 / sample_time
        for port_number0 in range(self.ports):
            try:
                port_number = port_number0 + 1
                current_data[f"port_{port_number}_traffic_rx"] = (
                    0
                    if (self._previous_data["traffic_rx"][port_number0] == 0)
                    else (
                        current_data["traffic_rx"][port_number0]
                        - self._previous_data["traffic_rx"][port_number0]
                    )
                )
                current_data[f"port_{port_number}_traffic_tx"] = (
                    0
                    if (self._previous_data["traffic_tx"][port_number0] == 0)
                    else (
                        current_data["traffic_tx"][port_number0]
                        - self._previous_data["traffic_tx"][port_number0]
                    )
                )
                current_data[f"port_{port_number}_crc_errors"] = (
                    0
                    if (self._previous_data["crc_errors"][port_number0] == 0)
                    else (
                        current_data["crc_errors"][port_number0]
                        - self._previous_data["crc_errors"][port_number0]
                    )
                )
                current_data[f"port_{port_number}_sum_rx"] = current_data["sum_rx"][
                    port_number0
                ]
                current_data[f"port_{port_number}_sum_tx"] = current_data["sum_tx"][
                    port_number0
                ]
                current_data[f"port_{port_number}_speed_rx"] = int(
                    current_data[f"port_{port_number}_traffic_rx"] * sample_factor
                )
                current_data[f"port_{port_number}_speed_tx"] = int(
                    current_data[f"port_{port_number}_traffic_tx"] * sample_factor
                )
                current_data[f"port_{port_number}_speed_io"] = (
                    current_data[f"port_{port_number}_speed_rx"]
                    + current_data[f"port_{port_number}_speed_tx"]
                )

            except IndexError:
                _LOGGER.debug("IndexError at port_number0=%s", port_number0)
                continue

            # Lowpass-Filter
            keys = [
                "traffic_rx",
                "traffic_tx",
                "crc_errors",
                "speed_rx",
                "speed_tx",
                "speed_io",
            ]
            for key in keys:
                current_data[f"port_{port_number}_{key}"] = max(
                    current_data[f"port_{port_number}_{key}"], 0
                )

            # Access old data if value is 0
            port_status_is_connected = (
                switch_data.get(f"port_{port_number}_status") == "on"
            )
            if port_status_is_connected:
                keys = ["sum_rx", "sum_tx", "speed_io"]
                for key in keys:
                    if current_data[f"port_{port_number}_{key}"] < 0:
                        current_data[f"port_{port_number}_{key}"] = self._previous_data[
                            key
                        ][port_number0]
                        current_data[key][port_number0] = current_data[
                            f"port_{port_number}_{key}"
                        ]
                        _LOGGER.info(
                            "Fallback to previous data: port_nr=%s port_%s=%s",
                            port_number,
                            key,
                            current_data[f"port_{port_number}_{key}"],
                        )

            # Highpass-Filter (max 1e9 B/s = 1GB/s per port)
            hp_max_traffic = 1e9 / sample_factor
            current_data[f"port_{port_number}_traffic_rx"] = min(
                current_data[f"port_{port_number}_traffic_rx"], hp_max_traffic
            )
            current_data[f"port_{port_number}_traffic_tx"] = min(
                current_data[f"port_{port_number}_traffic_tx"], hp_max_traffic
            )
            current_data[f"port_{port_number}_crc_errors"] = min(
                current_data[f"port_{port_number}_crc_errors"], hp_max_traffic
            )

            # Highpass-Filter (max 1e9 B/s = 1GB/s per port)
            # speed is already normalized to 1s
            hp_max_speed = 1e9
            current_data[f"port_{port_number}_speed_rx"] = min(
                current_data[f"port_{port_number}_speed_rx"], hp_max_speed
            )
            current_data[f"port_{port_number}_speed_tx"] = min(
                current_data[f"port_{port_number}_speed_tx"], hp_max_speed
            )

            # Sum up all metrics in key dict
            for key in [
                "traffic_rx",
                "traffic_tx",
                "crc_errors",
                "speed_rx",
                "speed_tx",
            ]:
                current_data[f"sum_port_{key}"] += current_data[
                    f"port_{port_number}_{key}"
                ]

            current_data["sum_port_speed_io"] = (
                current_data["sum_port_speed_rx"] + current_data["sum_port_speed_tx"]
            )

            # set for later (previous data)
            current_data["speed_io"][port_number0] = current_data[
                f"port_{port_number}_speed_io"
            ]

    def _updated_switch_data(self, current_data: dict) -> dict:
        switch_data = {}
        for port_number in range(1, self.ports + 1):
            keys = [
                "traffic_rx",
                "traffic_tx",
                "speed_rx",
                "speed_tx",
                "speed_io",
                "sum_rx",
                "sum_tx",
            ]
            for key in keys:
                switch_data[f"port_{port_number}_{key}_mbytes"] = (
                    _from_bytes_to_megabytes(current_data[f"port_{port_number}_{key}"])
                )

        switch_data["sum_port_traffic_rx"] = _from_bytes_to_megabytes(
            current_data["sum_port_traffic_rx"]
        )
        switch_data["sum_port_traffic_tx"] = _from_bytes_to_megabytes(
            current_data["sum_port_traffic_tx"]
        )
        switch_data["sum_port_speed_rx"] = _from_bytes_to_megabytes(
            current_data["sum_port_speed_rx"]
        )
        switch_data["sum_port_speed_tx"] = _from_bytes_to_megabytes(
            current_data["sum_port_speed_tx"]
        )
        switch_data["sum_port_speed_io"] = _from_bytes_to_megabytes(
            current_data["sum_port_speed_io"]
        )

        switch_data[f"port_{port_number}_crc_errors"] = current_data[
            f"port_{port_number}_crc_errors"
        ]
        switch_data["sum_port_crc_errors"] = current_data["sum_port_crc_errors"]
        return switch_data

    def _get_poe_port_config(self) -> dict:
        response = self.fetch_page_from_templates(
            self.switch_model.POE_PORT_CONFIG_TEMPLATES
        )
        return self._page_parser.parse_poe_port_config(response)

    def _get_poe_port_status(self) -> dict:
        response = self.fetch_page_from_templates(
            self.switch_model.POE_PORT_STATUS_TEMPLATES
        )
        return self._page_parser.parse_poe_port_status(response)

    def _get_port_status(self) -> dict:
        switch_data = {}
        if self._is_json_api:
            response_portstatus = self._json_api_fetch(
                self.switch_model.PORT_STATUS_TEMPLATES
            )
        else:
            response_portstatus = self.fetch_page_from_templates(
                self.switch_model.PORT_STATUS_TEMPLATES
            )
        port_status = self._page_parser.parse_port_status(
            response_portstatus, self.ports
        )

        for port_number in range(1, self.ports + 1):
            if len(port_status) == self.ports:
                switch_data[f"port_{port_number}_status"] = (
                    "on"
                    if port_status[port_number].get("status") in PORT_STATUS_CONNECTED
                    else "off"
                )
                switch_data[f"port_{port_number}_modus_speed"] = (
                    port_status[port_number].get("modus_speed") in PORT_MODUS_SPEED
                )
                port_connection_speed = (
                    port_status[port_number].get("connection_speed").upper()
                )
                port_connection_speeds = {
                    "10G": 10000,
                    "5G": 5000,
                    "2.5G": 2500,
                    "1G": 1000,
                    "1000M": 1000,
                    "100M": 100,
                    "10M": 10,
                }
                if port_connection_speed in port_connection_speeds:
                    switch_data[f"port_{port_number}_connection_speed"] = (
                        port_connection_speeds[port_connection_speed]
                    )
                else:
                    switch_data[f"port_{port_number}_connection_speed"] = 0
                if port_status[port_number].get("description") is not None:
                    switch_data[f"port_{port_number}_description"] = port_status[
                        port_number
                    ].get("description")
                if port_status[port_number].get("flow_control") is not None:
                    switch_data[f"port_{port_number}_flow_control"] = port_status[
                        port_number
                    ].get("flow_control")
            else:
                message = (
                    f"Number of statusses ({len(port_status)})"
                    f" not equal to number of ports({self.ports})"
                )
                raise InvalidPortStatusError(message)
        return switch_data

    def switch_leds(self, state: str) -> bool:
        """Switch poe port on or off."""
        if not self.switch_model.SWITCH_LED_TEMPLATES:
            message = "No LED templates found."
            raise NotImplementedError(message)
        if state not in SWITCH_STATES:
            message = f'State "{state}" not in {SWITCH_STATES}.'
            raise InvalidSwitchStateError(message)
        for template in self.switch_model.SWITCH_LED_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_switch_led_data(state)  # type: ignore[report-call-issue]
            self._page_fetcher.set_data_from_template(template, self, data)
            _LOGGER.debug("switch_leds data=%s", data)
            response = BaseResponse
            try:
                response = self._page_fetcher.request(method, url, data)
            except NotLoggedInError as error:
                if self.get_login_cookie():
                    response = self._page_fetcher.request(method, url, data)
                else:
                    message = "Not logged in and unable to login."
                    raise LoginFailedError(message) from error
            if (
                self._page_fetcher.has_ok_status(response)
                and str(response.content.strip()) == "b'SUCCESS'"
            ):
                # Clear cached metadata to refetch led status on next poll
                self._loaded_switch_metadata = {}
                return True
            _LOGGER.warning(
                "NetgearSwitchConnector.switch_leds response was %s",
                response.content.strip(),
            )
        return False

    def turn_on_leds(self) -> bool:
        """Turn on front panel LEDs."""
        return self.switch_leds("on")

    def turn_off_leds(self) -> bool:
        """Turn off front panel LEDs."""
        return self.switch_leds("off")

    def switch_poe_port(self, poe_port: int, state: str) -> bool:
        """Switch poe port on or off."""
        if state not in SWITCH_STATES:
            message = f'State "{state}" not in {SWITCH_STATES}.'
            raise InvalidSwitchStateError(message)
        if poe_port in self.poe_ports:
            for template in self.switch_model.SWITCH_POE_PORT_TEMPLATES:
                url = template["url"].format(ip=self.host)
                method = template["method"]
                data = self.switch_model.get_switch_poe_port_data(poe_port, state)  # type: ignore[report-call-issue]
                self._page_fetcher.set_data_from_template(template, self, data)
                _LOGGER.debug("switch_poe_port data=%s", data)
                response = BaseResponse
                try:
                    response = self._page_fetcher.request(method, url, data)
                except NotLoggedInError as error:
                    if self.get_login_cookie():
                        response = self._page_fetcher.request(method, url, data)
                    else:
                        message = "Not logged in and unable to login."
                        raise LoginFailedError(message) from error
                if (
                    self._page_fetcher.has_ok_status(response)
                    and str(response.content.strip()) == "b'SUCCESS'"
                ):
                    return True
                _LOGGER.warning(
                    "NetgearSwitchConnector.switch_poe_port response was %s",
                    response.content.strip(),
                )
        else:
            message = f"Port {poe_port} not in {self.poe_ports}"
            raise InvalidPoEPortError(message)
        return False

    def turn_on_poe_port(self, poe_port: int) -> bool:
        """Turn on power of a PoE port."""
        return self.switch_poe_port(poe_port, "on")

    def turn_off_poe_port(self, poe_port: int) -> bool:
        """Turn off power of a PoE port."""
        return self.switch_poe_port(poe_port, "off")

    def power_cycle_poe_port(self, poe_port: int) -> bool:
        """Cycle the power of a PoE port."""
        if poe_port in self.poe_ports:
            for template in self.switch_model.CYCLE_POE_PORT_TEMPLATES:
                url = template["url"].format(ip=self.host)
                data = self.switch_model.get_power_cycle_poe_port_data(poe_port)  # type: ignore[report-call-issue]
                self._page_fetcher.set_data_from_template(template, self, data)
                response = Response
                method = template["method"]
                try:
                    response = self._page_fetcher.request(method, url, data)
                except NotLoggedInError as error:
                    if self.get_login_cookie():
                        response = self._page_fetcher.request(method, url, data)
                    else:
                        message = "Not logged in and unable to login."
                        raise LoginFailedError(message) from error

                if (
                    self._page_fetcher.has_ok_status(response)
                    and str(response.content.strip()) == "b'SUCCESS'"
                ):
                    return True
                _LOGGER.warning(
                    "NetgearSwitchConnector.power_cycle_poe_port response was %s",
                    response.content.strip(),
                )
        return False

    def switch_port(self, port: int, state: str) -> bool:
        """Enable or disable a regular port."""
        self._validate_switch_port_request(port, state)

        current_info = self.get_switch_infos()
        desc_key = f"port_{port}_description"
        flow_key = f"port_{port}_flow_control"

        for template in self.switch_model.SWITCH_PORT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]
            data = self.switch_model.get_switch_port_data(port, state)
            if desc_key in current_info:
                data["DESCRIPTION"] = current_info[desc_key]
            if flow_key in current_info:
                flow = _normalize_flow_control(current_info[flow_key])
                if flow is not None:
                    data["FLOW_CONTROL"] = flow
            self._page_fetcher.set_data_from_template(template, self, data)
            _LOGGER.debug("switch_port data=%s", data)
            response = self._request_switch_port_change(method, url, data)
            if (
                self._page_fetcher.has_ok_status(response)
                and str(response.content.strip()) == "b'SUCCESS'"
            ):
                return True
            pending_apply_delay = _get_pending_apply_delay(response)
            if pending_apply_delay is not None:
                with suppress(NetgearPlusPageParserError):
                    self._client_hash = self._page_parser.parse_client_hash(response)
                _LOGGER.info(
                    "NetgearSwitchConnector.switch_port change accepted, "
                    "waiting %.1fs for switch to apply it",
                    pending_apply_delay,
                )
                time.sleep(pending_apply_delay)
                return True
            _LOGGER.warning(
                "NetgearSwitchConnector.switch_port response was %s",
                response.content.strip(),
            )
        return False

    def turn_on_port(self, port: int) -> bool:
        """Enable a port (Auto)."""
        return self.switch_port(port, "on")

    def turn_off_port(self, port: int) -> bool:
        """Disable a port."""
        return self.switch_port(port, "off")

    def save_pages(self, path_prefix: str = "") -> None:
        """Save all pages to files for debugging."""
        if not self.switch_model or not self.switch_model.MODEL_NAME:
            self.autodetect_model()
        if not Path(path_prefix).exists():
            Path(path_prefix).mkdir(parents=True)
        for template in [
            *self.switch_model.SWITCH_INFO_TEMPLATES,
            *self.switch_model.PORT_STATUS_TEMPLATES,
            *self.switch_model.PORT_STATISTICS_TEMPLATES,
            *self.switch_model.POE_PORT_CONFIG_TEMPLATES,
            *self.switch_model.POE_PORT_STATUS_TEMPLATES,
        ]:
            url = template["url"].format(ip=self.host)
            try:
                response = self.fetch_page_from_templates([template])
            except PageNotLoadedError:
                _LOGGER.warning(
                    "NetgearSwitchConnector.save_pages could not download %s", url
                )
                continue
            if self._page_fetcher.has_ok_status(response):
                page_name = url.split("/")[-1] or DEFAULT_PAGE
                with Path(f"{path_prefix}/{page_name}").open("wb") as file:
                    file.write(response.content)

                if (
                    template in self.switch_model.SWITCH_INFO_TEMPLATES
                    and not self._client_hash
                ):
                    with suppress(NetgearPlusPageParserError):
                        self._client_hash = self._page_parser.parse_client_hash(
                            response
                        )

            else:
                _LOGGER.warning(
                    "NetgearSwitchConnector.save_pages failed with status %s for %s",
                    response.status_code,
                    url,
                )

    def save_autodetect_templates(self, path_prefix: str = "") -> None:
        """Save all pages used to detect the switch model to files for debugging."""
        # These pages should be called unauthenticated, so logout first
        if self.get_cookie() != (None, None):
            _LOGGER.debug("NetgearSwitchConnector.save_autodetect_templates logout")
            self.delete_login_cookie()
        for template in self.switch_model.AUTODETECT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            response = BaseResponse()
            with suppress(NotLoggedInError):
                response = self._page_fetcher.request("get", url)
            if self._page_fetcher.has_ok_status(response):
                page_name = url.split("/")[-1] or DEFAULT_PAGE
                with Path(f"{path_prefix}/{page_name}").open("wb") as file:
                    file.write(response.content)
