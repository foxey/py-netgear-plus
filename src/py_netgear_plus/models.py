"""Definitions of auto-detectable Switch models."""

from contextlib import suppress
from enum import Enum
from typing import ClassVar

from py_netgear_plus.utils import get_all_child_classes_list


class VLANMember(str, Enum):
    """
    Port membership state in an 802.1Q VLAN.

    The enum value is the single-character ports_config code (T/U/E).
    Use ``.name.capitalize()`` for a display label ("Tagged"/...).
    """

    TAGGED = "T"
    UNTAGGED = "U"
    EXCLUDED = "E"

    @property
    def web_code(self) -> str:
        """Code used in the switch HTML hidden-mem field."""
        return _MEMBER_WEB_CODE[self]

    @classmethod
    def from_web_code(cls, code: str) -> "VLANMember":
        """Build from switch HTML hidden-mem code (1/2/3)."""
        return _WEB_CODE_TO_MEMBER[code]


_MEMBER_WEB_CODE = {
    VLANMember.TAGGED: "1",
    VLANMember.UNTAGGED: "2",
    VLANMember.EXCLUDED: "3",
}
_WEB_CODE_TO_MEMBER = {v: k for k, v in _MEMBER_WEB_CODE.items()}


class MultipleModelsDetectedError(Exception):
    """Detection of switch model was not unique."""


class SwitchModelNotDetectedError(Exception):
    """None of the models passed the tests."""


class PortNumberOutofRangeError(Exception):
    """Port number out of range."""


class InvalidCryptFunctionError(Exception):
    """No implementation for the defined CRYPT_FUNCTION."""


class UnknownVLANModeError(Exception):
    """VLAN mode is not recognized."""


class InvalidAdvancedVLANActionError(Exception):
    """Action is not recognized or have incorrect parameters."""


class InvalidVLANVoiceCoSError(Exception):
    """Voice CoS is invalid."""


class AutodetectedSwitchModel:
    """Base class definition for Netgear Plus Switch Models."""

    SUPPORTED = True
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]
    MODEL_NAME = ""
    PORTS = 0
    POE_PORTS: ClassVar = []
    POE_MAX_POWER_ALL_PORTS = None
    POE_MAX_POWER_SINGLE_PORT = None
    POE_SCHEDULING = False
    API_TYPE: ClassVar = ""
    CHECKS_AND_RESULTS: ClassVar = []

    AUTODETECT_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/login.cgi"},
        {"method": "get", "url": "http://{ip}/login.htm"},
        {"method": "get", "url": "http://{ip}/"},
    ]

    CRYPT_FUNCTION: ClassVar = "merge_hash"
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/login.cgi",
        "params": {"password": "_password_hash"},
    }

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/switch_info.htm"},
        {"method": "get", "url": "http://{ip}/switch_info.cgi"},
    ]
    SWITCH_LED_TEMPLATES: ClassVar = []
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/portStatistics.cgi",
            "params": {"hash": "_client_hash"},
        },
        {
            "method": "post",
            "url": "http://{ip}/port_statistics.htm",
            "params": {"hash": "_client_hash"},
        },
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/status.htm",
            "params": {"hash": "_client_hash"},
        }
    ]
    SWITCH_PORT_TEMPLATES: ClassVar = []
    POE_PORT_CONFIG_TEMPLATES: ClassVar = []
    SWITCH_POE_PORT_TEMPLATES: ClassVar = []
    CYCLE_POE_PORT_TEMPLATES: ClassVar = []
    POE_PORT_STATUS_TEMPLATES: ClassVar = []
    LOGOUT_TEMPLATES: ClassVar = [{"method": "post", "url": "http://{ip}/logout.cgi"}]
    SWITCH_REBOOT_TEMPLATES: ClassVar = []
    VLAN_STATUS_TEMPLATES: ClassVar = []
    VLAN_MODE_SET_TEMPLATES: ClassVar = []
    VLAN_ADVANCED_SET_TEMPLATES: ClassVar = []
    VLAN_PVID_SET_TEMPLATES: ClassVar = []
    PORT_SETTINGS_TEMPLATES: ClassVar = []
    IP_CONFIG_TEMPLATES: ClassVar = []
    IP_CONFIG_SET_TEMPLATES: ClassVar = []
    PASSWORD_CHANGE_TEMPLATES: ClassVar = []
    INITIAL_PASSWORD_HASH_TEMPLATES: ClassVar = []

    def __init__(self) -> None:
        """Empty contructor."""

    def get_autodetect_funcs(self) -> list:
        """Return list with detection functions."""
        return self.CHECKS_AND_RESULTS

    def get_switch_port_data(self, port: int, state: str) -> dict:
        """Return dict with form fields for switching a port (enable/disable)."""
        del port, state
        return {}

    def get_switch_poe_port_data(self, poe__port: int, state: str) -> dict:
        """Return empty dict. Implement on model level."""
        del poe__port, state
        return {}

    def get_power_cycle_poe_port_data(self, poe_port: int) -> dict:
        """Return empty dict. Implement on model level."""
        del poe_port
        return {}

    def has_led_switch(self) -> bool:
        """Return true when front panel LED can be switched."""
        return bool(self.SWITCH_LED_TEMPLATES)

    def get_switch_led_data(self, state: str) -> dict:
        """Return empty dict. Implement on model level."""
        del state
        return {}

    def get_vlan_mode_data(self, mode: str) -> dict:
        """Return empty dict. Implement on model level."""
        del mode
        return {}

    def get_advanced_vlan_data(  # noqa: PLR0913
        self,
        action: str,
        vlan_id: int,
        vlan_name: str | None = None,
        ports_config: str | list | None = None,
        voice_vlan: bool = False,  # noqa: FBT001, FBT002
        voice_cos: int = 6,
    ) -> dict:
        """Return empty dict. Implement on model level."""
        del action
        del vlan_id
        del vlan_name
        del ports_config
        del voice_vlan
        del voice_cos
        return {}

    def get_pvid_data(self, port_idx: int, vlan_id: int) -> dict:
        """Return empty dict. Implement on model level."""
        del port_idx
        del vlan_id
        return {}

    def has_reboot_button(self) -> bool:
        """Return true when switch reboot is supported."""
        return bool(self.SWITCH_REBOOT_TEMPLATES)

    def has_vlan_support(self) -> bool:
        """Return true when VLAN management is supported."""
        return bool(
            self.VLAN_STATUS_TEMPLATES
            and self.VLAN_MODE_SET_TEMPLATES
            and self.VLAN_ADVANCED_SET_TEMPLATES
            and self.VLAN_PVID_SET_TEMPLATES
        )

    def has_port_naming(self) -> bool:
        """Return true when ports can be renamed."""
        return bool(self.PORT_SETTINGS_TEMPLATES)

    def has_ip_config(self) -> bool:
        """Return true when IP/DHCP can be read or changed."""
        return bool(self.IP_CONFIG_TEMPLATES and self.IP_CONFIG_SET_TEMPLATES)

    def has_password_change(self) -> bool:
        """Return true when the admin password can be changed."""
        return bool(self.PASSWORD_CHANGE_TEMPLATES)

    def get_password_change_data(self, old_password: str, new_password: str) -> dict:
        """Build form data for change_password.cgi (Base64-encoded passwords)."""
        import base64  # noqa: PLC0415

        return {
            "oldPasswd": base64.b64encode(old_password.encode()).decode(),
            "newPasswd": base64.b64encode(new_password.encode()).decode(),
        }

    def get_ip_config_data(
        self,
        dhcp: bool,  # noqa: FBT001
        ip_address: str,
        subnet_mask: str,
        gateway: str,
    ) -> dict:
        """Build form data for ip_dhcp.cgi POST."""
        return {
            "dhcpMode": "1" if dhcp else "0",
            "ip_address": ip_address,
            "subnet_mask": subnet_mask,
            "gateway_address": gateway,
        }

    def get_port_settings_data(  # noqa: PLR0913
        self,
        port: int,
        description: str,
        speed: int,
        flow_control: int,
        ingress_rate: int,
        egress_rate: int,
        priority: int,
    ) -> dict:
        """Build form data for the port_status.cgi POST."""
        return {
            f"port{port}": "checked",
            "DESCRIPTION": description,
            "SPEED": str(speed),
            "FLOW_CONTROL": str(flow_control),
            "IngressRate": str(ingress_rate),
            "EgressRate": str(egress_rate),
            "priority": str(priority),
        }


class GS105E(AutodetectedSwitchModel):
    """Definition for Netgear GS105E model."""

    MODEL_NAME = "GS105E"
    PORTS = 5
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS105E"]),
    ]


class GS105Ev2(AutodetectedSwitchModel):
    """Definition for Netgear GS105Ev2 model."""

    MODEL_NAME = "GS105Ev2"
    PORTS = 5
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS105Ev2"]),
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/portStatistics.cgi",
        }
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/status.cgi",
        }
    ]
    SWITCH_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/status.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]
    SWITCH_REBOOT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/device_reboot.cgi",
            "params": {"CBox": "literal:on", "hash": "_client_hash"},
        }
    ]
    LOGOUT_TEMPLATES: ClassVar = [{"method": "get", "url": "http://{ip}/logout.cgi"}]

    def get_switch_port_data(self, port: int, state: str) -> dict:
        """Build form data for switching port state via SPEED field."""
        return {
            f"port{port}": "checked",
            "SPEED": 1 if state == "on" else 2,
        }


class GS105PE(GS105Ev2):
    """Definition for Netgear GS105PE model. Inherits port switching from GS105Ev2."""

    MODEL_NAME = "GS105PE"
    PORTS = 5
    SWITCH_REBOOT_TEMPLATES: ClassVar = []
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS105PE"]),
    ]


class GS108E(AutodetectedSwitchModel):
    """Definition for Netgear GS108E model."""

    MODEL_NAME = "GS108E"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS108E"]),
        (
            "parse_login_switchinfo_tag",
            ["GS308E - 8-Port Gigabit Ethernet Smart Managed Plus Switch"],
        ),
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS108Ev3(AutodetectedSwitchModel):
    """Definition for Netgear GS108Ev3 model."""

    MODEL_NAME = "GS108Ev3"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS108Ev3"]),
        (
            "parse_login_switchinfo_tag",
            [
                "GS108Ev3 - 8-Port Gigabit ProSAFE Plus Switch",
                "GS108Ev3 - 8-Port Gigabit Ethernet Smart Managed Plus Switch",
            ],
        ),
    ]
    SWITCH_REBOOT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/device_reboot.cgi",
            "params": {"CBox": "literal:on", "hash": "_client_hash"},
        }
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS108Ev4(AutodetectedSwitchModel):
    """Definition for Netgear GW108Ev4 model."""

    MODEL_NAME = "GS108Ev4"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS108Ev4"]),
    ]
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/dashboard.cgi"}
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/dashboard.cgi"}
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/portStatistics.cgi",
            "params": {"hash": "_client_hash"},
        },
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS108PEv3(AutodetectedSwitchModel):
    """Definition for Netgear GS108PEv3 model."""

    MODEL_NAME = "GS108PEv3"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS108PEv3"]),
        (
            "parse_login_switchinfo_tag",
            [
                "GS108PEv3 - 8-Port Gigabit ProSAFE Plus Switch",
                "GS108PEv3 - 8-Port Gigabit Ethernet Smart Managed Plus Switch",
            ],
        ),
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS305E(AutodetectedSwitchModel):
    """Definition for Netgear GS305E model."""

    MODEL_NAME = "GS305E"
    PORTS = 5
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]

    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS305E"]),
    ]

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/switch_info.cgi"},
    ]

    PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/status.cgi"},
    ]

    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/portStatistics.cgi"},
    ]


class GS308E(AutodetectedSwitchModel):
    """Definition for Netgear GS308E model."""

    MODEL_NAME = "GS308E"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS308E"]),
        (
            "parse_login_switchinfo_tag",
            [
                "GS308E - 8-Port Gigabit ProSAFE Plus Switch",
                "GS308E - 8-Port Gigabit Ethernet Smart Managed Plus Switch",
            ],
        ),
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["GS108SID", "SID"]


class GS308Ev4(GS108Ev4):
    """Definition for Netgear GS308Ev3 model."""

    MODEL_NAME = "GS308Ev4"
    PORTS = 8
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS308Ev4"]),
    ]
    SWITCH_REBOOT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/device_reboot.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]


class EMxSeries(AutodetectedSwitchModel):
    """Parent class definition for Netgear GSxxxEMX and XSxxxEM models."""

    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/homepage.html",
        "params": {"LoginPassword": "_password_hash"},
    }
    ALLOWED_COOKIE_TYPES: ClassVar = ["gambitCookie"]
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/sysInfo.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/port_settings.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/interface_stats.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    LOGOUT_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/logout.html",
            "params": {"Gambit": "_gambit"},
        }
    ]


class GS110EMX(EMxSeries):
    """Definition for Netgear GS110EMX model."""

    MODEL_NAME = "GS110EMX"
    PORTS = 10
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS110EMX"]),
    ]


class XS512EM(EMxSeries):
    """Definition for Netgear XS512EM model."""

    MODEL_NAME = "XS512EM"
    PORTS = 12
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["XS512EM"]),
    ]


class GS30xSeries(AutodetectedSwitchModel):
    """Parent class definition for Netgear GS30x series."""

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/dashboard.cgi"}
    ]
    SWITCH_LED_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/port_led.cgi",
            "params": {"hash": "_client_hash"},
        }
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

    SWITCH_REBOOT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/device_reboot.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    VLAN_STATUS_TEMPLATES: ClassVar = [{"method": "get", "url": "http://{ip}/vlan.cgi"}]

    VLAN_MODE_SET_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/vlanMod.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    VLAN_ADVANCED_SET_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/8021qAdvanced.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    VLAN_PVID_SET_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/portPVID.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    PORT_SETTINGS_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/port_status.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    IP_CONFIG_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/ip_dhcp.cgi"}
    ]

    IP_CONFIG_SET_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/ip_dhcp.cgi",
            "params": {"hash": "_client_hash"},
        }
    ]

    PASSWORD_CHANGE_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/change_password.cgi",
            "params": {"hash": "_client_hash"},
            # In factory-default state the CGI 404s without this Referer;
            # harmless once a non-default password is set.
            "headers": {"Referer": "http://{ip}/index.cgi"},
        }
    ]

    # Used after first login on a factory-fresh switch, when the
    # regular dashboard.cgi page just redirects to /index.cgi and no
    # client_hash can be extracted from it.
    INITIAL_PASSWORD_HASH_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/changeDefPwdCk.cgi",
            "headers": {"Referer": "http://{ip}/index.cgi"},
        }
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

    def get_switch_led_data(self, state: str) -> dict:
        """Return empty dict. Implement on model level."""
        return {
            "portled": 0 if state == "on" else 2,
        }

    def get_vlan_mode_data(self, mode: str) -> dict:
        """Return empty dict. Implement on model level."""
        available_modes = ["noVlan", "bscPotBsd", "advPotBsd", "bsc8021Q", "adv8021Q"]
        try:
            mode = available_modes.index(mode)
        except ValueError as e:
            message = f'Mode "{mode}" not in {available_modes}.'
            raise UnknownVLANModeError(message) from e
        return {"VLAN_MOD": str(mode)}

    def get_advanced_vlan_data(  # noqa: PLR0913
        self,
        action: str,
        vlan_id: int,
        vlan_name: str | None = None,
        ports_config: str | list | None = None,
        voice_vlan: bool = False,  # noqa: FBT001, FBT002
        voice_cos: int = 6,
    ) -> dict:
        """Return empty dict. Implement on model level."""
        data = {"ACTION": action, "VLAN_ID": str(vlan_id)}
        if action in ["Add", "Apply"]:
            # There can only be one voice vlan, setting another one
            # will change it to current one.
            max_voice_cos = 7
            if voice_cos < 0 or voice_cos > max_voice_cos:
                message = f"CoS ({voice_cos}) is not in [0;7]."
                raise InvalidVLANVoiceCoSError(message)

            if not vlan_name:
                message = "A VLAN name is required when adding or updating VLAN."
                raise InvalidAdvancedVLANActionError(message)

            if not ports_config:
                message = "Port configuration is required when adding or updating VLAN."
                raise InvalidAdvancedVLANActionError(message)

            if isinstance(ports_config, list):
                ports_config = "".join(x[0] for x in ports_config)

            if isinstance(ports_config, str):
                # Already-numeric form ("1"/"2"/"3") is also accepted;
                # the isdigit() check below validates either way.
                with suppress(ValueError):
                    ports_config = "".join(VLANMember(c).web_code for c in ports_config)

            if not ports_config.isdigit():
                message = (
                    "Invalid format for port config "
                    "- there is leftover alpha characters."
                )
                raise InvalidAdvancedVLANActionError(message)

            if len(ports_config) != self.PORTS:
                message = (
                    "Invalid port config - there should "
                    f"be {self.PORTS} ports, received {len(ports_config)}."
                )
                raise InvalidAdvancedVLANActionError(message)

            data.update(
                {
                    "vlanNum": str(99),  # It seems like it is only used by the UI
                    "VLAN_NAME": vlan_name,
                    "hiddenMem": ports_config,
                    "voiceVLANID": str(int(voice_vlan)),
                    "voiceVlanCos": str(voice_cos),
                }
            )
            return data
        if action == "Delete":
            return data
        message = f'Action "{action}" is not a known or implemented command.'
        raise InvalidAdvancedVLANActionError(message)

    def get_pvid_data(self, port_idx: int, vlan_id: int) -> dict:
        """Return empty dict. Implement on model level."""
        if port_idx > self.PORTS or port_idx < 1:
            message = f"Invalid port, it should be between 1 and {self.PORTS}."
            raise PortNumberOutofRangeError(message)

        return {"PORT": str(port_idx), "PVID": str(vlan_id)}


class GS30xEPxSeries(GS30xSeries):
    """Parent class definition for Netgear GS30xEPx series."""

    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:
        """Fill dict with form fields for switching a PoE port."""
        return {
            "ACTION": "Apply",
            "portID": poe_port - 1,
            "ADMIN_MODE": 1 if state == "on" else 0,
            "PORT_PRIO": 0,
            "POW_MOD": 3,
            "POW_LIMT_TYP": 2,
            "DETEC_TYP": 2,
            "DISCONNECT_TYP": 2,
        }


class GS305EP(GS30xEPxSeries):
    """Definition for Netgear GS305EP model."""

    MODEL_NAME = "GS305EP"
    PORTS = 5
    POE_PORTS: ClassVar = [1, 2, 3, 4]
    POE_MAX_POWER_ALL_PORTS = 63
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS305EP"]),
    ]


class GS305EPP(GS30xEPxSeries):
    """Definition for Netgear GS305EPP model."""

    MODEL_NAME = "GS305EPP"
    PORTS = 5
    POE_PORTS: ClassVar = [1, 2, 3, 4]
    POE_MAX_POWER_ALL_PORTS = 120
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS305EPP"]),
    ]


class GS308EP(GS30xSeries):
    """Definition for Netgear GS308EP model."""

    MODEL_NAME = "GS308EP"
    PORTS = 8
    POE_PORTS: ClassVar = [1, 2, 3, 4, 5, 6, 7, 8]
    POE_MAX_POWER_ALL_PORTS = 62
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS308EP"]),
    ]


class GS308EPP(GS30xEPxSeries):
    """Definition for Netgear GS308EP model."""

    MODEL_NAME = "GS308EPP"
    PORTS = 8
    POE_PORTS: ClassVar = [1, 2, 3, 4, 5, 6, 7, 8]
    POE_MAX_POWER_ALL_PORTS = 123
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS308EPP"]),
    ]


class GS316Series(GS30xSeries):
    """Parent class definition for Netgear GS316xx models."""

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
    POE_SCHEDULING = False  # True
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/homepage.html",
        "params": {"LoginPassword": "_password_hash"},
    }
    ALLOWED_COOKIE_TYPES: ClassVar = ["gambitCookie"]
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/dashboard.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    SWITCH_LED_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/leds.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    PORT_STATUS_TEMPLATES: ClassVar = SWITCH_INFO_TEMPLATES
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/interface_stats.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    POE_PORT_CONFIG_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    SWITCH_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    CYCLE_POE_PORT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/poePortConf.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    POE_PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/poePortStatus.html",
            "params": {"Gambit": "_gambit", "GetData": "literal:TRUE"},
        }
    ]
    LOGOUT_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/iss/specific/logout.html",
            "params": {"Gambit": "_gambit"},
        }
    ]
    SWITCH_REBOOT_TEMPLATES: ClassVar = [
        {
            "method": "post",
            "url": "http://{ip}/iss/specific/sys_reload.html",
            "params": {"Gambit": "_gambit", "ACTION": "literal:Reload"},
        }
    ]

    # GS316* uses a different web UI (iss/specific/*.html) than the
    # GS305/308 family, so the GS30xSeries CGI endpoints + DOM
    # assumptions for VLAN, port-settings, IP/DHCP, and the password
    # change/factory-hash pages do not apply. Disable until verified
    # against the GS316 firmware.
    VLAN_STATUS_TEMPLATES: ClassVar = []
    VLAN_MODE_SET_TEMPLATES: ClassVar = []
    VLAN_ADVANCED_SET_TEMPLATES: ClassVar = []
    VLAN_PVID_SET_TEMPLATES: ClassVar = []
    PORT_SETTINGS_TEMPLATES: ClassVar = []
    IP_CONFIG_TEMPLATES: ClassVar = []
    IP_CONFIG_SET_TEMPLATES: ClassVar = []
    PASSWORD_CHANGE_TEMPLATES: ClassVar = []
    INITIAL_PASSWORD_HASH_TEMPLATES: ClassVar = []

    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:
        """Fill dict with form fields for switching a PoE port."""
        return {
            "TYPE": "submitPoe",
            "PORT_NO": poe_port,
            "POWER_LIMIT_VALUE": 300,
            "PRIORITY": "NOTSET",
            "POWER_MODE": "NOTSET",
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

    def get_switch_led_data(self, state: str) -> dict:
        """Return empty dict. Implement on model level."""
        return {
            "PORT_LED_STATUS": 1 if state == "on" else 0,
        }


class GS316EP(GS316Series):
    """Definition for Netgear GS316EP model."""

    MODEL_NAME = "GS316EP"
    POE_MAX_POWER_ALL_PORTS = 180
    POE_MAX_POWER_SINGLE_PORT = 30
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS316EP"]),
    ]


class GS316EPP(GS316EP):
    """Definition for Netgear GS316EPP model."""

    MODEL_NAME = "GS316EPP"
    POE_MAX_POWER_ALL_PORTS = 231
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GS316EPP"]),
    ]


class JGSxxxSeries(AutodetectedSwitchModel):
    """Parent class definition for Netgear JGSxxx models."""

    CRYPT_FUNCTION: ClassVar = "hex_hmac_md5"
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/login.htm",
        "params": {
            "submitId": "literal:pwdLogin",
            "password": "_password_hash",
            "submitEnd": "literal:",
        },
    }
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/config/status_switch_info.htm",
        },
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/config/status_status.htm",
        },
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {
            "method": "get",
            "url": "http://{ip}/config/monitoring_port_statistics.htm",
        }
    ]


class JGS516PE(JGSxxxSeries):
    """Definition for Netgear JGS516PE model."""

    MODEL_NAME = "JGS516PE"
    PORTS = 16
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [False]),
        ("parse_first_script_tag", ["JGS516PE"]),
    ]


class JGS524Ev2(JGSxxxSeries):
    """Definition for Netgear JGS524Ev2 model."""

    MODEL_NAME = "JGS524Ev2"
    PORTS = 24
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [False]),
        ("parse_first_script_tag", ["JGS524Ev2"]),
    ]


class GS116Ev2(JGSxxxSeries):
    """Definition for Netgear GS116Ev2 model."""

    MODEL_NAME = "GS116Ev2"
    PORTS = 16
    POE_PORTS: ClassVar = []
    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [False]),
        ("parse_first_script_tag", ["GS116Ev2"]),
    ]


class GSS108E(AutodetectedSwitchModel):
    """Definition for Netgear GSS108E model."""

    MODEL_NAME = "GSS108E"
    PORTS = 8
    POE_PORTS: ClassVar = []
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]

    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),
        ("parse_login_title_tag", ["GSS108E"]),
    ]

    # Mandatory request templates for interacting with the switch
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/login.cgi",
        "params": {"password": "_password_hash"},
    }

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/switch_info.cgi"},
    ]

    PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/status.cgi"},
    ]

    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/portStatistics.cgi"},
    ]

    LOGOUT_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/logout.cgi"},
    ]


class MS3xxSeries(AutodetectedSwitchModel):
    """Parent class definition for Netgear MS3xx series (JSON REST API)."""

    API_TYPE: ClassVar = "json_rest"
    CHECKS_AND_RESULTS: ClassVar = []
    AUTODETECT_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/api/system/status"},
    ]
    LOGIN_TEMPLATE: ClassVar = {
        "method": "patch",
        "url": "http://{ip}/api/system/login",
    }
    LOGIN_SESSION_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/api/login_session",
    }
    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/api/system/status"},
    ]
    PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/api/ports"},
    ]
    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/api/ports/statistics"},
    ]
    LOGOUT_TEMPLATES: ClassVar = []


class MS305E(MS3xxSeries):
    """Definition for Netgear MS305E model."""

    MODEL_NAME = "MS305E"
    PORTS = 5


class MS308E(MS3xxSeries):
    """Definition for Netgear MS308E model."""

    MODEL_NAME = "MS308E"
    PORTS = 8


MODELS = get_all_child_classes_list(AutodetectedSwitchModel, "MODEL_NAME")
