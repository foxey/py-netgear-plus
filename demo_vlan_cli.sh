#!/usr/bin/env bash
# Same walk-through using the ngp-cli binary.
# Each step waits for Enter. Port 1 stays on VLAN 1 (mgmt).

set -e

SWITCH_IP="10.156.22.73"
PASS='Password1!'

pause() {
  read -r -p $'\n--- '"$1"' (Enter to continue) --- ' _
}

status() {
  ngp-cli --json vlan status | jq '{mode, vlans, pvids: [.ports|to_entries[]|{p:.key, pvid:.value.pvid}]}'
}

# 0. Login once. Cookie cached in ~/.netgear_plus_cookie.
ngp-cli -P "$PASS" login "$SWITCH_IP"

pause "1. Read current VLAN status"
status

pause "2. Switch to advanced 802.1Q mode"
ngp-cli vlan mode adv8021Q
status

pause "3. Add VLAN 100 'Internal' (port 1 Excluded for mgmt safety)"
ngp-cli vlan add 100 Internal EUUUUUUU
status

pause "4. Move ports 2..7 onto VLAN 100 via PVID"
for p in 2 3 4 5 6 7; do
  ngp-cli vlan pvid "$p" 100
done
status

pause "5. Rename VLAN 100 to 'Servers' and exclude port 8"
ngp-cli vlan edit 100 Servers EUUUUUUE
status

pause "6. apply: declarative reconciliation (strict)"
cat > /tmp/vlan_desired.json <<'JSON'
{
  "mode": "adv8021Q",
  "vlans": {
    "1":   {"name": "Default", "ports_config": "UEEEEEEE"},
    "100": {"name": "Servers", "ports_config": "EUUUUUUU"},
    "200": {"name": "Guest",   "ports_config": "EUUUUUUU"}
  },
  "pvids": {"2":100, "3":100, "4":100, "5":200, "6":200, "7":200}
}
JSON
ngp-cli vlan apply /tmp/vlan_desired.json --strict
status

pause "7. Move PVIDs back to 1 and remove custom VLANs"
for p in 2 3 4 5 6 7; do
  ngp-cli vlan pvid "$p" 1
done
ngp-cli vlan remove 100
ngp-cli vlan remove 200
status

pause "8. Disable VLANs (back to noVlan)"
ngp-cli vlan mode noVlan
status

# --- Port naming ---

pause "9. List per-port settings"
ngp-cli port list

pause "10. Rename port 3 to 'Workshop' (port 1 is mgmt — leave alone)"
ngp-cli port rename 3 Workshop
ngp-cli port list | grep -E '^  3:'

pause "11. Clear port 3 name (restore)"
ngp-cli port rename 3 ""
ngp-cli port list | grep -E '^  3:'

# --- IP / DHCP ---

pause "12. Read IP/DHCP configuration"
ngp-cli --json network show

pause "13. Re-apply same static config (noop -- DANGEROUS: wrong values can strand the switch)"
read -r IP MASK GW < <(ngp-cli --json network show | jq -r '"\(.ip_address) \(.subnet_mask) \(.gateway)"')
ngp-cli network set --static "$IP" "$MASK" "$GW"
ngp-cli --json network show

# --- Password change (round-trip) ---

TEMP_PWD="Temp1234!"

pause "14. Change admin password to $TEMP_PWD"
ngp-cli -P "$PASS" password --new "$TEMP_PWD"

pause "Re-login with new password"
ngp-cli -P "$TEMP_PWD" login "$SWITCH_IP"
ngp-cli network show

pause "15. Change password back"
ngp-cli -P "$TEMP_PWD" password --new "$PASS"

pause "Re-login with original"
ngp-cli -P "$PASS" login "$SWITCH_IP"

echo
echo "Done."
