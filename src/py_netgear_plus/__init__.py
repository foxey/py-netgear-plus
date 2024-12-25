"""Netgear API."""

import logging
import time
from pathlib import Path
from typing import Any

import requests
import requests.cookies
from lxml import html
from lxml.html import HtmlElement

from . import models, netgear_crypt
from .fetcher import BaseResponse, PageNotLoadedError
from .parsers import PageParser, create_page_parser

__version__ = "0.2.14rc0"

SWITCH_STATES = ["on", "off"]
DEFAULT_PAGE = "index.htm"

API_V2_CHECKS = {
    "bootloader": ["V1.00.03", "V2.06.01", "V2.06.02", "V2.06.03"],
    "firmware": ["V2.06.24GR", "V2.06.24EN"],
}


def _from_bytes_to_megabytes(v: float) -> float:
    bytes_to_mbytes = 1e-6
    return float(f"{round(v * bytes_to_mbytes, 2):.2f}")


PORT_STATUS_CONNECTED = ["Aktiv", "Up", "UP", "CONNECTED"]
PORT_MODUS_SPEED = ["Auto"]


_LOGGER = logging.getLogger(__name__)


class LoginFailedError(Exception):
    """Invalid credentials."""


class MultipleModelsDetectedError(Exception):
    """Detection of switch model was not unique."""


class SwitchModelNotDetectedError(Exception):
    """None of the models passed the tests."""


class EmptyTemplateParameterError(Exception):
    """None of the models passed the tests."""


class InvalidSwitchStateError(Exception):
    """State should be one of the options in SWITCH_STATES."""


class InvalidPoEPortError(Exception):
    """Port is not a PoE port."""


class NetgearSwitchConnector:
    """Representation of a Netgear Switch."""

    LOGIN_URL_REQUEST_TIMEOUT = 15
    MAX_AUTHENTICATION_FAILURES = 3
    TRUE = "TRUE"

    def __init__(self, host: str, password: str) -> None:
        """Initialize Connector Object."""
        self.host = host

        # initial values
        self.switch_model = models.AutodetectedSwitchModel
        self.page_parser = PageParser()
        self.ports = 0
        self.poe_ports = []
        self._switch_bootloader = "unknown"

        # offline mode settings
        self.offline_mode = False
        self.offline_path_prefix = ""

        # sleep time between requests
        self.sleep_time = 0.25

        # Login related instance variables
        # plain login password
        self._password = password
        # response of login page request
        self._login_page_response = requests.Response()
        # rand value from login page
        self._rand = ""
        # cryped password if md5
        self._login_page_form_password = ""
        # cookie/hash data
        self.cookie_name = None
        self.cookie_content = None
        self._client_hash = ""
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

    def turn_on_offline_mode(self, path_prefix: str) -> None:
        """Turn on offline mode."""
        self.offline_mode = True
        self.offline_path_prefix = path_prefix

    def turn_on_online_mode(self) -> None:
        """Turn on online mode."""
        self.offline_mode = False

    def autodetect_model(self) -> type[models.AutodetectedSwitchModel]:
        """Detect switch model from login page contents."""
        _LOGGER.debug(
            "[NetgearSwitchConnector.autodetect_model] called for IP=%s", self.host
        )
        for template in models.AutodetectedSwitchModel.AUTODETECT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            method = template["method"]

            response = BaseResponse()
            if not self.offline_mode:
                response = requests.request(
                    method,
                    url,
                    allow_redirects=False,
                    timeout=self.LOGIN_URL_REQUEST_TIMEOUT,
                )
            else:
                response = self.get_page_from_file(url)

            if response and response.status_code == requests.codes.ok:
                self._login_page_response = response
                passed_checks_by_model = {}
                matched_models = []
                for mdl_cls in models.MODELS:
                    mdl = mdl_cls()
                    mdl_name = mdl.MODEL_NAME
                    passed_checks_by_model[mdl_name] = {}
                    autodetect_funcs = mdl.get_autodetect_funcs()
                    for func_name, expected_results in autodetect_funcs:
                        func_result = getattr(self, func_name)()
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
                        self.page_parser = create_page_parser(
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

    def _set_instance_attributes_by_model(
        self, switch_model: type[models.AutodetectedSwitchModel]
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

    def check_login_url(self) -> bool:
        """Request login page and saves response, checks for HTTP Status 200."""
        url = self.switch_model.LOGIN_TEMPLATE["url"].format(ip=self.host)
        _LOGGER.debug(
            "[NetgearSwitchConnector.check_login_url] calling request for url=%s", url
        )
        resp = requests.get(
            url, allow_redirects=False, timeout=self.LOGIN_URL_REQUEST_TIMEOUT
        )
        self._login_page_response = resp
        return resp.status_code == requests.codes.ok

    def check_login_form_rand(self) -> bool:
        """Check if login form contain hidden *rand* input."""
        if self._login_page_response is None or not self._login_page_response.content:
            return False
        tree = html.fromstring(self._login_page_response.content)
        input_rand_elems = tree.xpath('//input[@id="rand"]')
        if input_rand_elems:
            self._rand = input_rand_elems[0].value
            merged = netgear_crypt.merge(self._password, self._rand)
            md5_str = netgear_crypt.make_md5(merged)
            self._login_page_form_password = md5_str
            return True
        self._login_page_form_password = self._password
        return False

    def check_login_title_tag(self) -> str:
        """For new firmwares V2.06.10, V2.06.17, V2.06.24."""
        tree = html.fromstring(self._login_page_response.content)
        title_elems = tree.xpath("//title")
        if title_elems:
            return title_elems[0].text.replace("NETGEAR", "").strip()
        return ""

    def check_login_switchinfo_tag(self) -> str:
        """Return info tag or empty when not present."""
        """For old firmware V2.00.05, return """ ""
        """or something like: "GS108Ev3 - 8-Port Gigabit ProSAFE Plus Switch"."""
        """Newer firmwares contains that too."""
        tree = html.fromstring(self._login_page_response.content)
        switchinfo_elems = tree.xpath('//div[@class="switchInfo"]')
        if switchinfo_elems:
            return switchinfo_elems[0].text
        return ""

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

    def get_login_password(self) -> str:
        """Return the password in plain text or hashed depending on the model."""
        if self._login_page_form_password == "":
            if not self._login_page_response.content:
                self.check_login_url()
            self.check_login_form_rand()
        if self._rand:
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_login_password]"
                " returning password crypted with rand=%s",
                self._rand,
            )
        else:
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_login_password]"
                " returning password in plain text"
            )
        return self._login_page_form_password

    def get_login_cookie(self) -> bool:
        """Login and save returned cookie."""
        if not self.switch_model or self.switch_model.MODEL_NAME == "":
            self.autodetect_model()
        response = None
        login_password = self.get_login_password()
        template = self.switch_model.LOGIN_TEMPLATE
        url = template["url"].format(ip=self.host)
        method = template["method"]
        key = template["key"]
        _LOGGER.debug(
            "[NetgearSwitchConnector.get_login_cookie] calling requests.%s for url=%s",
            method,
            url,
        )
        response = requests.request(
            method,
            url,
            data={key: login_password},
            allow_redirects=True,
            timeout=self.LOGIN_URL_REQUEST_TIMEOUT,
        )
        if not response or response.status_code != requests.codes.ok:
            raise LoginFailedError

        _LOGGER.debug(
            "[NetgearSwitchConnector.get_login_cookie] looking for cookies: %s",
            ", ".join(self.switch_model.ALLOWED_COOKIE_TYPES),
        )
        # GS31xEP(P) series switches return the cookie value in a hidden form element
        gambit_tag = html.fromstring(response.content).xpath('//input[@name="Gambit"]')
        if gambit_tag:
            self.cookie_name = self.switch_model.ALLOWED_COOKIE_TYPES[0]
            self.cookie_content = gambit_tag[0].value
            _LOGGER.debug("[NetgearSwitchConnector.get_login_cookie] Found Gambit tag:")
            _LOGGER.debug(
                "[NetgearSwitchConnector.get_login_cookie] Setting cookie %s=%s",
                self.cookie_name,
                self.cookie_content,
            )
            return True
        # Other switches return a cookie on successful login
        for ct in self.switch_model.ALLOWED_COOKIE_TYPES:
            cookie = response.cookies.get(ct, None)
            if cookie:
                _LOGGER.debug(
                    "[NetgearSwitchConnector.get_login_cookie]" " Found cookie %s", ct
                )
                self.cookie_name = ct
                self.cookie_content = cookie
                self._authentication_failure_count = 0
                return True
        self.handle_soft_authentication_failure(response)
        return False

    def handle_soft_authentication_failure(self, response: requests.Response) -> None:
        """Handle soft authentication failure."""
        # Clear cached login data
        self._login_page_response = requests.Response()
        self._rand = ""
        self._login_page_form_password = ""

        if "content" not in dir(response):
            message = "No content in login form response."
            raise LoginFailedError(message)
        tree = html.fromstring(response.content)

        # Handling Error Messages
        error_msg = None
        if isinstance(self.switch_model, (models.GS30xSeries)):
            error_msg = tree.xpath('//div[@class="pwdErrStyle"]')
            if error_msg:
                error_msg = error_msg[0].text
        else:
            error_msg = tree.xpath('//input[@id="err_msg"]')
            if error_msg:
                error_msg = error_msg[0].value
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
        if self._authentication_failure_count >= self.MAX_AUTHENTICATION_FAILURES:
            count = self._authentication_failure_count
            message = f"Too many authentication failures ({count})."
            raise LoginFailedError(message)

    def _is_authenticated(self, response: requests.Response | BaseResponse) -> bool:
        """Check for redirect to login when not authenticated (anymore)."""
        if "content" in dir(response):
            title = html.fromstring(response.content).xpath("//title")
            if len(title) and title[0].text.lower() == "redirect to login":
                _LOGGER.warning(
                    "[NetgearSwitchConnector._is_authenticated]"
                    " Returning false: title=%s",
                    title[0].text.lower(),
                )
                return False
            script = html.fromstring(response.content).xpath(
                '//script[contains(text(),"/wmi/login")]'
            )
            if len(script) and 'top.location.href = "/wmi/login"' in script[0].text:
                _LOGGER.warning(
                    "[NetgearSwitchConnector._is_authenticated]"
                    " Returning false: script=%s",
                    script[0].text,
                )
                return False
        return True

    def delete_login_cookie(self) -> bool:
        """Logout and delete cookie."""
        """Only used while testing. Prevents "Maximum number of sessions" error."""
        try:
            response = self.fetch_page(self.switch_model.LOGOUT_TEMPLATES)
        except requests.exceptions.ConnectionError:
            self.cookie_name = None
            self.cookie_content = None
            return True
        else:
            _LOGGER.debug(
                "[NetgearSwitchConnector.delete_login_cookie] "
                "logout response status code=%s",
                response.status_code,
            )
            return response.status_code == requests.codes.ok

    def _request(
        self,
        method: str,
        url: str,
        data: Any = None,
        timeout: int = 0,
        allow_redirects: bool = False,  # noqa: FBT001, FBT002
    ) -> requests.Response:
        if not self.cookie_name or not self.cookie_content:
            success = self.get_login_cookie()
            if not success:
                raise LoginFailedError
        if timeout == 0:
            timeout = self.LOGIN_URL_REQUEST_TIMEOUT
        jar = requests.cookies.RequestsCookieJar()
        if self.cookie_name and self.cookie_content:
            jar.set(self.cookie_name, self.cookie_content, domain=self.host, path="/")
        _LOGGER.debug(
            "[NetgearSwitchConnector._request] calling requests.%s for url=%s",
            method,
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
            time.sleep(self.sleep_time)
            self.get_login_cookie()
            response = self._request(method, url, data, timeout, allow_redirects)
        return response

    def fetch_page(self, templates: list) -> requests.Response | BaseResponse:
        """Return response for 1st successful request from templates."""
        response = BaseResponse()
        for template in templates:
            url = template["url"].format(ip=self.host)
            if not self.offline_mode:
                method = template["method"]
                data = {}
                self._set_data_from_template(template, data)
                response = self._request(method, url, data)
            else:
                response = self.get_page_from_file(url)
            if response.status_code == requests.codes.ok:
                break
        if response.status_code != requests.codes.ok:
            message = f"Failed to load any page of templates: {templates}"
            raise PageNotLoadedError(message)
        return response

    def _set_data_from_template(
        self, template: dict[str, Any], data: dict[str, Any]
    ) -> None:
        """Populate data from template using class variables."""
        if "params" not in template:
            return
        for key, value in template["params"].items():
            try:
                data[key] = getattr(self, value)
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

    def _parse_poe_port_config(self, tree: HtmlElement) -> dict:
        config_by_port = {}
        poe_port_power_x = tree.xpath('//input[@id="hidPortPwr"]')
        for i, x in enumerate(poe_port_power_x):
            config_by_port[i + 1] = "on" if x.value == "1" else "off"
        return config_by_port

    def _parse_poe_port_status(self, tree: HtmlElement) -> dict:
        poe_output_power = {}
        # Port name:
        #   //li[contains(@class,"poe_port_list_item")]
        #       //span[contains(@class,"poe_index_li_title")]
        # Power mode:
        #   //li[contains(@class,"poe_port_list_item")]
        #       //span[contains(@class,"poe-power-mode")]
        # Port status:
        #   //li[contains(@class,"poe_port_list_item")]
        #       //div[contains(@class,"poe_port_status")]
        poe_output_power_x = tree.xpath(
            '//li[contains(@class,"poe_port_list_item")]//div[contains(@class,"poe_port_status")]'
        )
        for i, x in enumerate(poe_output_power_x):
            try:
                poe_output_power[i + 1] = float(x.xpath(".//span")[5].text)
            except ValueError:
                poe_output_power[i + 1] = 0.0
        return poe_output_power

    def _get_gs3xx_switch_info(self, tree: HtmlElement, text: str) -> str:
        span_node = tree.xpath(f'//span[text()="{text}"]')
        if span_node:
            for child_span in (
                span_node[0].getparent().getnext().iterchildren(tag="span")
            ):
                return child_span.text
        return ""

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

        if not self.offline_mode:
            sample_time = _start_time - self._previous_timestamp
        else:
            sample_time = 0
        switch_data["response_time_s"] = round(sample_time, 1)

        self._update_current_data(current_data, switch_data, sample_time)

        switch_data.update(self._updated_switch_data(current_data))

        # Partially supported models fail parsing below this line
        if not self.switch_model.SUPPORTED:
            return switch_data

        if isinstance(self.switch_model, (models.GS30xSeries)):
            time.sleep(self.sleep_time)
            switch_data.update(self._get_poe_port_status())

        # set previous data
        self._previous_timestamp = time.perf_counter()
        self._previous_data = current_data

        return switch_data

    def _get_switch_metadata(self) -> None:
        if not self.switch_model:
            self.autodetect_model()
        page = self.fetch_page(self.switch_model.SWITCH_INFO_TEMPLATES)
        if not page.content:
            return

        self._client_hash = self.page_parser.parse_client_hash(page)

        # Avoid a second call on next get_switch_infos() call
        self._loaded_switch_metadata = {
            "switch_ip": self.host
        } | self.page_parser.parse_switch_metadata(page)

    def _get_port_statistics(self) -> dict[str, Any]:
        response = self.fetch_page(self.switch_model.PORT_STATISTICS_TEMPLATES)
        return self.page_parser.parse_port_statistics(response, self.ports)

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
                    current_data["traffic_rx"][port_number0]
                    - self._previous_data["traffic_rx"][port_number0]
                )
                current_data[f"port_{port_number}_traffic_tx"] = (
                    current_data["traffic_tx"][port_number0]
                    - self._previous_data["traffic_tx"][port_number0]
                )
                current_data[f"port_{port_number}_crc_errors"] = (
                    current_data["crc_errors"][port_number0]
                    - self._previous_data["crc_errors"][port_number0]
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
                    if current_data[f"port_{port_number}_{key}"] <= 0:
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

    def _get_poe_port_status(self) -> dict:
        switch_data = {}
        response_poeportconfig = self.fetch_page(
            self.switch_model.POE_PORT_CONFIG_TEMPLATES
        )
        tree_poeportconfig = html.fromstring(response_poeportconfig.content)
        poe_port_config = self._parse_poe_port_config(tree=tree_poeportconfig)

        for poe_port_nr, poe_power_config in poe_port_config.items():
            switch_data[f"port_{poe_port_nr}_poe_power_active"] = poe_power_config
        time.sleep(self.sleep_time)
        response_poeportstatus = self.fetch_page(
            self.switch_model.POE_PORT_STATUS_TEMPLATES
        )
        tree_poeportstatus = html.fromstring(response_poeportstatus.content)
        poe_port_status = self._parse_poe_port_status(tree=tree_poeportstatus)

        for poe_port_nr, poe_power_status in poe_port_status.items():
            switch_data[f"port_{poe_port_nr}_poe_output_power"] = poe_power_status
        return switch_data

    def _get_port_status(self) -> dict:
        switch_data = {}
        response_portstatus = self.fetch_page(self.switch_model.PORT_STATUS_TEMPLATES)
        port_status = self.page_parser.parse_port_status(
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
                port_connection_speed = port_status[port_number].get("connection_speed")
                port_connection_speeds = {"1000M": 1000, "100M": 100, "10M": 10}
                if port_connection_speed in port_connection_speeds:
                    switch_data[f"port_{port_number}_connection_speed"] = (
                        port_connection_speeds[port_connection_speed]
                    )
                else:
                    switch_data[f"port_{port_number}_connection_speed"] = 0
        return switch_data

    def switch_poe_port(self, poe_port: int, state: str) -> bool:
        """Switch poe port on or off."""
        if state not in SWITCH_STATES:
            message = f'State "{state}" not in {SWITCH_STATES}.'
            raise InvalidSwitchStateError(message)
        if poe_port in self.poe_ports:
            for template in self.switch_model.SWITCH_POE_PORT_TEMPLATES:
                url = template["url"].format(ip=self.host)
                data = self.switch_model.get_switch_poe_port_data(poe_port, state)  # type: ignore[report-call-issue]
                self._set_data_from_template(template, data)
                _LOGGER.debug("switch_poe_port data=%s", data)
                resp = self._request("post", url, data=data)
                if (
                    resp.status_code == requests.codes.ok
                    and str(resp.content.strip()) == "b'SUCCESS'"
                ):
                    return True
                _LOGGER.warning(
                    "NetgearSwitchConnector.switch_poe_port response was %s",
                    resp.content.strip(),
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
                self._set_data_from_template(template, data)
                resp = self._request(template["method"], url, data=data)
                if (
                    resp.status_code == requests.codes.ok
                    and str(resp.content.strip()) == "b'SUCCESS'"
                ):
                    return True
                _LOGGER.warning(
                    "NetgearSwitchConnector.power_cycle_poe_port response was %s",
                    resp.content.strip(),
                )
        return False

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
                response = self.fetch_page([template])
            except PageNotLoadedError:
                _LOGGER.warning(
                    "NetgearSwitchConnector.save_pages could not download %s", url
                )
                continue
            if response.status_code == requests.codes.ok and (
                self._is_authenticated(response)
            ):
                page_name = url.split("/")[-1] or DEFAULT_PAGE
                with Path(f"{path_prefix}/{page_name}").open("wb") as file:
                    file.write(response.content)
            else:
                _LOGGER.warning(
                    "NetgearSwitchConnector.save_pages failed with status %s for %s",
                    response.status_code,
                    url,
                )
            time.sleep(self.sleep_time)
        # The pages should be called unauthenticated, so self.fetch_page is not used
        for template in self.switch_model.AUTODETECT_TEMPLATES:
            url = template["url"].format(ip=self.host)
            response = requests.get(
                url,
                timeout=self.LOGIN_URL_REQUEST_TIMEOUT,
            )
            if response.status_code == requests.codes.ok:
                page_name = url.split("/")[-1] or DEFAULT_PAGE
                with Path(f"{path_prefix}/{page_name}").open("wb") as file:
                    file.write(response.content)
