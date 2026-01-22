#!/usr/bin/env python3
"""
Walk through the VLAN library API against a real GS308EP.

Each step pauses for Enter. Keeps port 1 on VLAN 1 (mgmt link).
"""

import json
from pprint import pprint

import py_netgear_plus

IP = "10.156.22.73"
PASSWORD = "Password1!"


def pause(label: str) -> None:
    input(f"\n--- {label} (Enter to continue) ---")


def show_status(sw: py_netgear_plus.NetgearSwitchConnector) -> None:
    status = sw.vlan_status()
    print("mode:", status["mode"])
    print("vlans:")
    pprint(status["vlans"])
    print("pvids:", {p: info["pvid"] for p, info in status["ports"].items()})


sw = py_netgear_plus.NetgearSwitchConnector(IP, PASSWORD)
sw.autodetect_model()
sw.get_login_cookie()
sw.get_switch_infos()
print(f"Connected to {sw.switch_model.MODEL_NAME} at {IP}")

pause("1. Read current VLAN status")
show_status(sw)

pause("2. Switch to advanced 802.1Q mode")
sw.set_vlan_mode("adv8021Q")
show_status(sw)

pause("3. Add VLAN 100 'Internal' (port 1 Excluded for mgmt safety)")
sw.add_vlan(100, vlan_name="Internal", ports_config="EUUUUUUU")
show_status(sw)

pause("4. Move ports 2..7 onto VLAN 100 via PVID")
for port in range(2, 8):
    sw.set_vlan_pvid(port, 100)
show_status(sw)

pause("5. Rename VLAN 100 to 'Servers' and exclude port 8")
sw.edit_vlan(100, vlan_name="Servers", ports_config="EUUUUUUE")
show_status(sw)

pause("6. apply_vlan_config: declarative reconciliation (strict)")
desired = {
    "mode": "adv8021Q",
    "vlans": {
        1: {"name": "Default", "ports_config": "U" + "E" * 7},
        100: {"name": "Servers", "ports_config": "EUUUUUUU"},
        200: {"name": "Guest", "ports_config": "EUUUUUUU"},
    },
    "pvids": dict.fromkeys(range(2, 5), 100) | dict.fromkeys(range(5, 8), 200),
}
summary = sw.apply_vlan_config(desired, strict=True)
print("summary:")
print(json.dumps(summary, indent=2, default=str))
show_status(sw)

pause("7. Move PVIDs back to 1 and remove custom VLANs")
for port in range(2, 8):
    sw.set_vlan_pvid(port, 1)
sw.remove_vlan(100)
sw.remove_vlan(200)
show_status(sw)

pause("8. Disable VLANs (back to noVlan)")
sw.set_vlan_mode("noVlan")
show_status(sw)

# --- Port naming ---


def show_ports(sw: py_netgear_plus.NetgearSwitchConnector) -> None:
    for p, s in sw.get_port_settings().items():
        print(
            f"  {p}: name={s['name']!r} speed={s['speed']} "
            f"in={s['ingress_rate']} out={s['egress_rate']} "
            f"flow={s['flow_control']}"
        )


pause("9. Read per-port settings")
print(f"has_port_naming: {sw.switch_model.has_port_naming()}")
show_ports(sw)

pause("10. Rename port 3 to 'Workshop' (port 1 is mgmt — leave alone)")
sw.set_port_name(3, "Workshop")
show_ports(sw)

pause("11. Clear port 3 name (restore)")
sw.set_port_name(3, "")
show_ports(sw)

# --- IP / DHCP ---

pause("12. Set switch to DHCP")
print(f"has_ip_config: {sw.switch_model.has_ip_config()}")
sw.set_ip_config(dhcp=True)
cfg = sw.get_ip_config()
print(cfg)

pause(
    "13. Re-apply same static config (noop — DANGEROUS: changing values "
    "may strand your management connection)"
)
sw.set_ip_config(
    dhcp=False,
    ip_address=cfg["ip_address"],
    subnet_mask=cfg["subnet_mask"],
    gateway=cfg["gateway"],
)
print(sw.get_ip_config())

# --- Password change (round-trip) ---

TEMP_PWD = "Temp1234!"

pause(f"14. Change admin password to {TEMP_PWD!r}")
print(f"has_password_change: {sw.switch_model.has_password_change()}")
sw.change_password(PASSWORD, TEMP_PWD)
# change_password updates sw._password; subsequent calls reuse it.
# Session was invalidated on the switch side — a fresh login is needed.
sw2 = py_netgear_plus.NetgearSwitchConnector(IP, TEMP_PWD)
sw2.autodetect_model()
sw2.get_login_cookie()
sw2.get_switch_infos()
print("Logged back in with new password.")

pause("15. Change password back to original")
sw2.change_password(TEMP_PWD, PASSWORD)
print("Password restored.")

print("\nDone.")
