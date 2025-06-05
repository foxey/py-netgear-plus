"""Unit tests for the py_netgear_plus __init__ module."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests
import requests.cookies
from py_netgear_plus import (
    DEFAULT_PAGE,
    NetgearSwitchConnector,
    _from_bytes_to_megabytes,
)
from py_netgear_plus.fetcher import URL_REQUEST_TIMEOUT, BaseResponse
from py_netgear_plus.models import (
    GS105PE,
    GS110EMX,
    GS305E,
    GS308E,
    GS308EP,
    GS308EPP,
    GS316EPP,
    JGS516PE,
    XS512EM,
    AutodetectedSwitchModel,
    GS105Ev2,
    GS108Ev3,
    GS108Ev4,
    GS108PEv3,
    GS308Ev4,
    JGS524Ev2,
)
from py_netgear_plus.netgear_crypt import hex_hmac_md5, merge_hash

# List of models with saved pages, extracted rand values and crypted passwords
MODEL_PARAMETERS = [
    (GS105Ev2, "897006492", "6e5b60b4082b2ac23103ec2e7caf0284", "<html></html>"),
    (GS105PE, "1578591883", "99915f464feee3be4193edd6dcc6b9b3", "<html></html>"),
    (GS108Ev3, "1763184457", "c2c905d5d99f592106a378bf709b737a", "<html></html>"),
    (GS108PEv3, "1735414426", "2038fc386c5e77ded19b31d7aa14a443", "<html></html>"),
    (
        GS110EMX,
        "2055460636",
        "3e51baecfd84e4c0010662d6d92a1253",
        '<html><input name="Gambit" value="cookie_value"></html>',
    ),
    (GS108Ev4, "1798387901", "0b9b21bb5c28b73e300cfb526d468bd9", "<html></html>"),
    (GS305E, "1018767543", "c01909066125ac45d275af0a6cd09b5e", "<html></html>"),
    (GS308E, "2102219470", "e8e0a9820f683fe8e64da0014a49902c", "<html></html>"),
    (GS308EP, "990464497", "43001294a37a3f2e1f919b64072a1a32", "<html></html>"),
    (GS308EPP, "1425622205", "e65ad5ee60718843afafeaa03bd1ec49", "<html></html>"),
    (
        GS316EPP,
        "1127757600",
        "3c630eb52109743e94ef671e137b3de0",
        '<html><input name="Gambit" value="cookie_value"></html>',
    ),
    (
        GS308Ev4,
        "1467252539",
        "5f01444681a83b9a39c6e9e1ea2a91db",
        "<html></html>",
    ),
    (
        JGS516PE,
        None,
        "26fe7cce1e480dd05e7f76155579d3ed",
        "<html></html>",
    ),
    (
        JGS524Ev2,
        None,
        "26fe7cce1e480dd05e7f76155579d3ed",
        "<html></html>",
    ),
    (
        XS512EM,
        "1113244551",
        "6ca0965e7a44ee17eec5d575c8c56dd8",
        '<html><input name="Gambit" value="cookie_value"></html>',
    ),
]
# Add models without a full set of pages with pytest.param(GSXYZ,
#   marks=pytest.mark.xfail(reason="no valid data pages"))
MODELS_FOR_GET_SWITCH_INFOS = [
    GS105Ev2,
    GS105PE,
    GS108Ev3,
    GS108PEv3,
    GS108Ev4,
    GS110EMX,
    GS305E,
    GS308E,
    GS308EP,
    GS308EPP,
    GS308Ev4,
    GS316EPP,
    JGS516PE,
    JGS524Ev2,
    XS512EM,
]

# List of models for reboot test, with
# reboot response code and if page content is returned
MODELS_FOR_REBOOT = [(GS108Ev3, 200, True), (GS308Ev4, 444, False)]

TEST_MODELS = [model[0] for model in MODEL_PARAMETERS]


class PyTestPageFetcher:
    """A class to fetch pages from a file."""

    def __init__(self, switch_model: type[AutodetectedSwitchModel]) -> None:
        """Initialize the PageFetcher."""
        self.switch_model = switch_model
        self._sequence = 0

    def next_sequence(self) -> int:
        """Get the next sequence number."""
        self._sequence += 1
        return self._sequence

    def from_file(
        self,
        templates: list[dict[str, str]],
        client_hash: str = "",
    ) -> requests.Response:
        """Fetch a page from a file."""
        del client_hash
        response = Mock()
        response.status_code = requests.codes.ok
        response.content = self.get_path(templates).read_bytes()
        return response

    def get_path(self, templates: list[dict[str, str]]) -> Path:
        """Get the path to the first page that exists as a file."""
        for template in templates:
            url = template["url"]
            page_name = url.split("/")[-1] or DEFAULT_PAGE
            path = Path(
                f"pages/{self.switch_model.MODEL_NAME}/{self._sequence}/{page_name}"
            )
            if path.exists():
                return path
        raise FileNotFoundError


def test_0_from_bytes_to_megabytes() -> None:
    """Test cases for _from_bytes_to_megabytes function."""
    assert _from_bytes_to_megabytes(1000000) == 1.00
    assert _from_bytes_to_megabytes(5000000) == 5.00
    assert _from_bytes_to_megabytes(123456789) == 123.46
    assert _from_bytes_to_megabytes(0) == 0.00
    assert _from_bytes_to_megabytes(-1000000) == -1.00


def test_0_netgear_switch_connector_initialization() -> None:
    """Test initialization of NetgearSwitchConnector."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    assert connector.host == "192.168.0.1"
    assert connector._password == "password"
    assert connector.switch_model is not None
    assert connector.ports == 0
    assert connector.poe_ports == []
    assert connector._switch_bootloader == "unknown"
    assert connector.sleep_time == 0.25
    assert connector._page_fetcher is not None
    assert connector._client_hash is None
    assert connector._gambit is None
    assert connector._previous_data == {}
    assert connector._loaded_switch_metadata == {}


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_autodetect_model(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test autodetect_model method."""
    page_fetcher = PyTestPageFetcher(switch_model)
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_check_login_url(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test check_login_url method."""
    page_fetcher = PyTestPageFetcher(switch_model)
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        assert connector._page_fetcher.check_login_url(switch_model) is True
        assert connector._page_fetcher._login_page_response == mock_response
        checks = switch_model.CHECKS_AND_RESULTS
        if True in next(
            (check[1] for check in checks if check[0] == "check_login_form_rand"),
            [False],
        ):
            rand = connector._page_parser.parse_login_form_rand(
                connector._page_fetcher._login_page_response
            )
            assert rand is not None


@pytest.mark.parametrize(
    ("switch_model", "rand", "crypted_password", "content"),
    MODEL_PARAMETERS,
)
def test_parse_login_form_rand(
    switch_model: type[AutodetectedSwitchModel],
    rand: str,
    crypted_password: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test check_login_form_rand method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    connector._page_fetcher._login_page_response = Mock()

    page_fetcher = PyTestPageFetcher(switch_model)
    with page_fetcher.get_path(switch_model.AUTODETECT_TEMPLATES).open() as file:
        connector._page_fetcher._login_page_response.content = file.read()

    connector._page_fetcher._login_page_response.status_code = requests.codes.ok
    assert (
        connector._page_parser.parse_login_form_rand(
            connector._page_fetcher._login_page_response
        )
        == rand
    )
    crypt_function = switch_model.CRYPT_FUNCTION
    if crypt_function == "hex_hmac_md5":
        assert hex_hmac_md5(password) == crypted_password
    elif crypt_function == "merge_hash":
        assert merge_hash(password, rand) == crypted_password
    else:
        pytest.fail(f"Unknown crypt function {crypt_function}")


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_get_unique_id(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test get_unique_id method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
    connector.switch_model = switch_model
    assert (
        connector.get_unique_id()
        == f"{connector.switch_model.__name__.lower()}_192_168_0_1"
    )


@pytest.mark.parametrize(
    ("switch_model", "rand", "crypted_password", "content"),
    MODEL_PARAMETERS,
)
def test_get_login_password(
    switch_model: AutodetectedSwitchModel,
    rand: str,
    crypted_password: str,
    content: str,  # noqa: ARG001
) -> None:
    """Test get_login_password method."""
    password = "Password1"
    connector = NetgearSwitchConnector(host="192.168.0.1", password=password)
    with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
        mock_response = Mock()
        page_name = switch_model.LOGIN_TEMPLATE["url"].split("/")[-1] or DEFAULT_PAGE
        with Path(f"pages/{switch_model.MODEL_NAME}/0/{page_name}").open() as file:
            mock_response.content = file.read()
        mock_response.status_code = requests.codes.ok
        mock_request.return_value = mock_response
        connector._page_fetcher._login_page_response = mock_response
        crypt_function = switch_model.CRYPT_FUNCTION
        if crypt_function == "hex_hmac_md5":
            assert hex_hmac_md5(password) == crypted_password
        elif crypt_function == "merge_hash":
            assert merge_hash(password, rand) == crypted_password
        else:
            pytest.fail(f"Unknown crypt function {crypt_function}")


@pytest.mark.parametrize(
    ("switch_model", "rand", "crypted_password", "content"),
    MODEL_PARAMETERS,
)
def test_get_login_cookie(
    switch_model: AutodetectedSwitchModel,
    rand: str,
    crypted_password: str,  # noqa: ARG001
    content: str,
) -> None:
    """Test get_login_cookie method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="Password1")
    connector.turn_on_offline_mode(f"pages/{switch_model.MODEL_NAME}/0")
    connector.autodetect_model()
    connector._page_fetcher.check_login_url(connector.switch_model)
    connector.turn_on_online_mode()

    key = next(
        (
            k
            for k, v in connector.switch_model.LOGIN_TEMPLATE["params"].items()
            if v == "_password_hash"
        ),
        None,
    )

    crypt_function = switch_model.CRYPT_FUNCTION
    if crypt_function == "hex_hmac_md5":
        data = {
            "submitId": "pwdLogin",
            key: hex_hmac_md5(connector._password),
            "submitEnd": "",
        }
    elif crypt_function == "merge_hash":
        data = {
            key: merge_hash(connector._password, rand),
        }
    else:
        pytest.fail(f"Unknown crypt function {crypt_function}")

    with (
        patch("py_netgear_plus.fetcher.requests.request") as mock_request,
    ):
        mock_response = Mock()
        mock_response.status_code = requests.codes.ok
        mock_response.content = content
        mock_response.cookies.get.return_value = "cookie_value"
        mock_request.return_value = mock_response
        assert connector.get_login_cookie() is True
        mock_request.assert_called()
        mock_request.assert_called_with(
            connector.switch_model.LOGIN_TEMPLATE["method"],
            connector.switch_model.LOGIN_TEMPLATE["url"].format(ip=connector.host),
            data=data,
            allow_redirects=True,
            timeout=URL_REQUEST_TIMEOUT,
        )
        (cookie_name, cookie_value) = connector.get_cookie()
        assert cookie_name is not None
        assert cookie_value == "cookie_value"


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        ("GS108Ev3/0/index.htm", True),
        ("GS308EP/unauthenticated.html", False),
        ("GS308EP/0/dashboard.cgi", True),
        ("GS308EP/0/portStatistics.cgi", True),
        ("GS308EPP/0/dashboard.cgi", True),
        ("GS308EPP/0/portStatistics.cgi", True),
        ("GS316EPP/unauthenticated.html", False),
        ("GS316EPP/0/dashboard.html", True),
    ],
)
def test_is_authenticated(page: str, expected: bool) -> None:  # noqa: FBT001
    """Test is_authenticated method."""
    connector = NetgearSwitchConnector(host="192.168.0.1", password="XXXXXXXX")
    response = Mock()
    response.content = Path(f"pages/{page}").read_text()
    response.status_code = requests.codes.ok
    assert connector._page_fetcher._is_authenticated(response) is expected


@pytest.mark.parametrize(
    "switch_model",
    MODELS_FOR_GET_SWITCH_INFOS,
)
def test_get_switch_infos(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test initialization of NetgearSwitchConnector."""
    with (
        patch("py_netgear_plus.time.perf_counter", return_value=0),
        patch(
            "py_netgear_plus.NetgearSwitchConnector.fetch_page_from_templates"
        ) as mock_fetch_page_from_templates,
    ):
        page_fetcher = PyTestPageFetcher(switch_model)
        mock_fetch_page_from_templates.side_effect = page_fetcher.from_file
        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")
        with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)
        connector._page_fetcher._login_page_response = Mock()
        with page_fetcher.get_path([switch_model.LOGIN_TEMPLATE]).open() as file:
            connector._page_fetcher._login_page_response.content = file.read()
        for sequence in range(2):
            connector._page_fetcher._login_page_response.status_code = requests.codes.ok
            switch_data = connector.get_switch_infos()
            with Path(
                f"pages/{switch_model.MODEL_NAME}/{sequence}/switch_infos.json"
            ).open() as file:
                validation_data = json.loads(file.read())
                assert switch_data == validation_data
            page_fetcher.next_sequence()


@pytest.mark.parametrize(
    "switch_model",
    TEST_MODELS,
)
def test_turn_on_and_off_poe_port(switch_model: type[AutodetectedSwitchModel]) -> None:
    """Test turning on/off power on a PoE port."""
    with (
        patch(
            "py_netgear_plus.NetgearSwitchConnector.fetch_page_from_templates"
        ) as mock_fetch_page_from_templates,
    ):
        page_fetcher = PyTestPageFetcher(switch_model)
        mock_fetch_page_from_templates.side_effect = page_fetcher.from_file

        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")

        with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)
        assert isinstance(connector.switch_model.POE_PORTS, list)
        if len(connector.switch_model.POE_PORTS) == 0:
            pytest.skip(f"Model {switch_model.MODEL_NAME} has no PoE ports.")

        connector._client_hash = "client_hash"
        connector._gambit = "gambit"
        connector.set_cookie("cookie_name", "cookie_value")

        response = BaseResponse()
        response.status_code = requests.codes.ok
        response.content = b"SUCCESS"
        with patch(
            "py_netgear_plus.fetcher.requests.request",
            return_value=response,
        ) as mock_request:
            cookies = requests.cookies.RequestsCookieJar()
            cookies.set(
                str(connector.get_cookie()[0]),
                str(connector.get_cookie()[1]),
                domain=connector.host,
                path="/",
            )

            mock_request.return_value = response

            for state in ["on", "off"]:
                poe_port = connector.switch_model.POE_PORTS[0]
                data = connector.switch_model.get_switch_poe_port_data(poe_port, state)
                connector._page_fetcher.set_data_from_template(
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0], connector, data
                )
                connector.switch_poe_port(poe_port, state)
                mock_request.assert_called()
                mock_request.assert_called_with(
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0]["method"],
                    connector.switch_model.SWITCH_POE_PORT_TEMPLATES[0]["url"].format(
                        ip=connector.host
                    ),
                    data=data,
                    cookies=cookies,
                    timeout=URL_REQUEST_TIMEOUT,
                    allow_redirects=False,
                )


@pytest.mark.parametrize(
    ("switch_model", "status_code", "has_content"),
    MODELS_FOR_REBOOT,
)
def test_reboot(
    switch_model: type[AutodetectedSwitchModel],
    status_code: int,
    has_content: bool,  # noqa: FBT001
) -> None:
    """Test switch reboot."""
    if not switch_model.SWITCH_REBOOT_TEMPLATES:
        pytest.skip(f"Model {switch_model.MODEL_NAME} does not support reboot.")

    assert switch_model.SWITCH_REBOOT_TEMPLATES

    with (
        patch(
            "py_netgear_plus.NetgearSwitchConnector.fetch_page_from_templates"
        ) as mock_fetch_page_from_templates,
    ):
        page_fetcher = PyTestPageFetcher(switch_model)
        mock_fetch_page_from_templates.side_effect = page_fetcher.from_file

        connector = NetgearSwitchConnector(host="192.168.0.1", password="password")

        with patch("py_netgear_plus.fetcher.requests.request") as mock_request:
            mock_response = Mock()
            with page_fetcher.get_path(
                switch_model.AUTODETECT_TEMPLATES
            ).open() as file:
                mock_response.content = file.read()
            mock_response.status_code = requests.codes.ok
            mock_request.return_value = mock_response
            connector.autodetect_model()
        assert isinstance(connector.switch_model, switch_model)

        connector._client_hash = "client_hash"
        connector._gambit = "gambit"
        connector.set_cookie("cookie_name", "cookie_value")

        response = Mock()
        response.status_code = status_code

        # some switches don't return any content on a reboot, thus
        # we need to have the ability to not load a page
        if has_content:
            with page_fetcher.get_path(
                switch_model.SWITCH_REBOOT_TEMPLATES
            ).open() as file:
                response.content = file.read()
        else:
            response.content = None

        with patch(
            "py_netgear_plus.fetcher.requests.request",
            return_value=response,
        ) as mock_request:
            cookies = requests.cookies.RequestsCookieJar()
            cookies.set(
                str(connector.get_cookie()[0]),
                str(connector.get_cookie()[1]),
                domain=connector.host,
                path="/",
            )

            mock_request.return_value = response

            data = {}
            connector._page_fetcher.set_data_from_template(
                connector.switch_model.SWITCH_REBOOT_TEMPLATES[0], connector, data
            )

            assert connector.reboot() is True

            mock_request.assert_called()
            mock_request.assert_called_with(
                connector.switch_model.SWITCH_REBOOT_TEMPLATES[0]["method"],
                connector.switch_model.SWITCH_REBOOT_TEMPLATES[0]["url"].format(
                    ip=connector.host
                ),
                data=data,
                cookies=cookies,
                timeout=URL_REQUEST_TIMEOUT,
                allow_redirects=False,
            )


if __name__ == "__main__":
    pytest.main()
