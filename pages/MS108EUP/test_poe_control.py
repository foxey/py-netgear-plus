#!/usr/bin/env python3
"""
Test PoE control on MS108EUP switch.

This script will:
1. Show current PoE status for all ports
2. Let you pick a port to test
3. Turn PoE OFF for that port (device loses power!)
4. Wait 5 seconds
5. Turn PoE back ON

WARNING: This will cut power to whatever device is on that port!
         Pick a port with a non-critical device for testing.
"""

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from py_netgear_plus import NetgearSwitchConnector


def test_poe_control(ip: str, password: str):
    """Test PoE control functionality."""

    print(f"\n{'='*60}")
    print("MS108EUP PoE Control Test")
    print(f"{'='*60}\n")

    # Connect and login
    print("[1/6] Connecting and logging in...")
    api = NetgearSwitchConnector(ip, password)
    api.autodetect_model()
    print(f"       Model: {api.switch_model.MODEL_NAME}")

    # Try login up to 3 times (switch may have session limits)
    login_result = False
    for attempt in range(3):
        login_result = api.get_login_cookie()
        print(f"       Login attempt {attempt + 1}: {login_result}")
        if login_result:
            break
        print("       Retrying...")
        time.sleep(1)

    print(f"       Gambit set: {api._gambit is not None}")
    if api._gambit:
        print(f"       Gambit value: {api._gambit[:20]}...")
        print("       ✓ Connected")
    else:
        print("       ✗ Login failed - Gambit not obtained")
        print("\n       Possible causes:")
        print("       - Too many active sessions on the switch")
        print("       - Password might be incorrect")
        print("       - Try logging out from the web interface first")
        return False

    # Get current status
    print("\n[2/6] Getting current PoE status...")
    info = api.get_switch_infos()

    print("\n       Current PoE Status:")
    print("       " + "-"*40)
    for port in range(1, 9):
        status = info.get(f"port_{port}_poe_power_active", "?")
        power = info.get(f"port_{port}_poe_output_power", 0)
        indicator = "⚡" if power > 0 else "  "
        print(f"       {indicator} Port {port}: {status:3} ({power:5.1f}W)")
    print("       " + "-"*40)

    # Ask which port to test
    print("\n[3/6] Select a port to test...")
    print("       ⚠️  WARNING: This will cut power to the device on that port!")
    print("       Choose a port with a non-critical device (e.g., a test device)")
    print()

    while True:
        try:
            port_input = input("       Enter port number (1-8) or 'q' to quit: ").strip()
            if port_input.lower() == 'q':
                print("\n       Cancelled. No changes made.")
                return True
            port = int(port_input)
            if 1 <= port <= 8:
                break
            print("       Please enter a number between 1 and 8")
        except ValueError:
            print("       Please enter a valid number")

    # Confirm
    power = info.get(f"port_{port}_poe_output_power", 0)
    if power > 0:
        print(f"\n       ⚠️  Port {port} is currently drawing {power}W")
        confirm = input("       Are you sure you want to test this port? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("\n       Cancelled. No changes made.")
            return True

    # Turn OFF
    print(f"\n[4/6] Turning OFF PoE on port {port}...")
    try:
        api.turn_off_poe_port(port)
        print("       ✓ PoE turned OFF")
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Wait
    print("\n[5/6] Waiting 5 seconds...")
    for i in range(5, 0, -1):
        print(f"       {i}...", end=" ", flush=True)
        time.sleep(1)
    print()

    # Turn ON
    print(f"\n[6/6] Turning ON PoE on port {port}...")
    try:
        api.turn_on_poe_port(port)
        print("       ✓ PoE turned ON")
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Verify
    print("\n       Verifying final status...")
    time.sleep(2)
    info = api.get_switch_infos()
    status = info.get(f"port_{port}_poe_power_active", "?")
    power = info.get(f"port_{port}_poe_output_power", 0)
    print(f"       Port {port}: {status} ({power}W)")

    print(f"\n{'='*60}")
    print("✓ PoE control test complete!")
    print(f"{'='*60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(description="Test PoE control on MS108EUP")
    parser.add_argument("--ip", required=True, help="Switch IP address")
    parser.add_argument("--password", required=True, help="Switch password")
    args = parser.parse_args()

    success = test_poe_control(args.ip, args.password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
