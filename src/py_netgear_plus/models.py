"""Definitions of auto-detectable Switch models."""

from typing import ClassVar


class PortNumberOutofRangeError(Exception):
    """Port number out of range."""


class AutodetectedSwitchModel:
    """Netgear Plus Switch Model Definition."""

    SUPPORTED = True
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]
    MODEL_NAME = ""
    PORTS = 0
    POE_PORTS: ClassVar = []
    POE_MAX_POWER_ALL_PORTS = None
    POE_MAX_POWER_SINGLE_PORT = None
    POE_SCHEDULING = False
    CHECKS_AND_RESULTS: ClassVar = []

    AUTODETECT_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/login.cgi"},
        {"method": "get", "url": "http://{ip}/login.htm"},
        {"method": "get", "url": "http://{ip}/"},
    ]

    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/login.cgi",
        "key": "password",
    }

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/switch_info.htm"},
        {"method": "get", "url": "http://{ip}/switch_info.cgi"},
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/portStatistics.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/status.htm",
            "params": {"hash": "_client_hash"},
        }
    ]
    POE_PORT_CONFIG_TEMPLATES: ClassVar = []
    SWITCH_POE_PORT_TEMPLATES: ClassVar = []
    CYCLE_POE_PORT_TEMPLATES: ClassVar = []
    POE_PORT_STATUS_TEMPLATES: ClassVar = []
    LOGOUT_TEMPLATES: ClassVar = [{"method": "post", "url": "http://{ip}/logout.cgi"}]

    def __init__(self) -> None:
        """Empty contructor."""

    def get_autodetect_funcs(self) -> list:
        """Return list with detection functions."""
        return self.CHECKS_AND_RESULTS

    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:  # noqa: ARG002
        """Return empty dict. Implement on model level."""
        return {}

    def get_power_cycle_poe_port_data(self, poe_port: int) -> dict:  # noqa: ARG002
        """Return empty dict. Implement on model level."""
        return {}


class GS105E(AutodetectedSwitchModel):
    """Definition for Netgear GS105E model."""

    MODEL_NAME = "GS105E"
    PORTS = 5
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS105E"]),
    ]


class GS105Ev2(AutodetectedSwitchModel):
    """Definition for Netgear CG105Ev2 model."""

    MODEL_NAME = "GS105Ev2"
    PORTS = 5
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS105Ev2"]),
    ]


class GS108E(AutodetectedSwitchModel):
    """Definition for Netgear GS108E model."""

    MODEL_NAME = "GS108E"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS108E"]),
        (
            "check_login_switchinfo_tag",
            ["GS308E - 8-Port Gigabit Ethernet Smart Managed Plus Switch"],
        ),
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS108Ev3(AutodetectedSwitchModel):
    """Definition for Netgear GW108Ev3 model."""

    MODEL_NAME = "GS108Ev3"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS108Ev3"]),
        (
            "check_login_switchinfo_tag",
            [
                "GS108Ev3 - 8-Port Gigabit ProSAFE Plus Switch",
                "GS108Ev3 - 8-Port Gigabit Ethernet Smart Managed Plus Switch",
            ],
        ),
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS30xSeries(AutodetectedSwitchModel):
    """Parent class definition for Netgear GS3xx series."""

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/dashboard.cgi"}
    ]
    PORT_STATUS_TEMPLATES: ClassVar = SWITCH_INFO_TEMPLATES
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/portStatistics.cgi"}
    ]
    POE_PORT_CONFIG_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/PoEPortConfig.cgi"}
    ]
    SWITCH_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/PoEPortConfig.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]
    CYCLE_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/PoEPortConfig.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]
    POE_PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/getPoePortStatus.cgi"}
    ]

    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:
        """Fill dict with form fields for switching a PoE port."""
        return {
            "ACTION": "Apply",
            "portID": poe_port - 1,
            "ADMIN_MODE": 1 if state == "on" else 0,
            "PORT_PRIO": 0,
            "POW_MOD": 3,
            "POW_LIMT_TYP": 0,
            "DETEC_TYP": 2,
            "DISCONNECT_TYP": 2,
        }

    def get_power_cycle_poe_port_data(self, poe_port: int) -> dict:
        """Return empty dict. Implement on model level."""
        return {
            "ACTION": "Reset",
            "port" + str(poe_port - 1): "checked",
        }


class GS305EP(GS30xSeries):
    """Definition for Netgear GS305EP model."""

    MODEL_NAME = "GS305EP"
    PORTS = 5
    POE_PORTS: ClassVar = [1, 2, 3, 4]
    POE_MAX_POWER_ALL_PORTS = 63
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS305EP"]),
    ]


class GS308EP(GS30xSeries):
    """Definition for Netgear GS308EP model."""

    MODEL_NAME = "GS308EP"
    PORTS = 8
    POE_PORTS: ClassVar = [1, 2, 3, 4, 5, 6, 7, 8]
    POE_MAX_POWER_ALL_PORTS = 62
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS308EP"]),
    ]


class GS316EP(GS30xSeries):
    """Definition for Netgear GS316EP model."""

    SUPPORTED = False
    MODEL_NAME = "GS316EP"
    PORTS = 16
    POE_PORTS: ClassVar = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
    ]
    POE_MAX_POWER_ALL_PORTS = None  # 180
    POE_MAX_POWER_SINGLE_PORT = None  # 30
    POE_SCHEDULING = False  # True
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS316EP"]),
    ]
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/homepage.html",
        "key": "LoginPassword",
    }
    ALLOWED_COOKIE_TYPES: ClassVar = ["gambitCookie"]
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/dashboard.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]
    PORT_STATUS_TEMPLATES: ClassVar = SWITCH_INFO_TEMPLATES
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/interface_stats.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]
    POE_PORT_CONFIG_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]
    SWITCH_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]
    CYCLE_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]
    POE_PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/poePortStatus.html",
            "params": {"Gambit": "cookie_content", "GetData": "TRUE"},
        }
    ]
    LOGOUT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/logout.html",
            "params": {"Gambit": "cookie_content"},
        }
    ]

    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:
        """Fill dict with form fields for switching a PoE port."""
        return {
            "TYPE": "submitPoe",
            "PORT_NO": poe_port - 1,
            "POWER_LIMIT_VALUE": 300,
            "PRIORITY": "NOTSET",
            "PWER_MODE": "NOTSET",
            "POWER_LIMIT_TYPE": "NOTSET",
            "DETECTION": "NOTSET",
            "ADMIN_STATE": 1 if state == "on" else 0,
            "DISCONNECT_TYPE": "NOTSET",
        }

    def get_power_cycle_poe_port_data(self, poe_port: int) -> dict:
        """Return form fields for PoE port cycle."""
        if poe_port not in self.POE_PORTS:
            message = f"Port number {poe_port} out of range."
            raise PortNumberOutofRangeError(message)
        poeport_string = ["0"] * len(self.POE_PORTS)
        poeport_string[poe_port - 1] = "1"
        return {
            "TYPE": "resetPoe",
            "PoePort": "".join(poeport_string),
        }


class GS316EPP(GS316EP):
    """Definition for Netgear GS316EPP model."""

    MODEL_NAME = "GS316EPP"
    POE_POWER_ALL_PORTS = 231
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("check_login_title_tag", ["GS316EPP"]),
    ]


MODELS = [
    GS105E,
    GS105Ev2,
    GS108E,
    GS108Ev3,
    GS305EP,
    GS308EP,
    GS316EP,
    GS316EPP,
]
