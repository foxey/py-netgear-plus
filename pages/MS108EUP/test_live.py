#!/usr/bin/env python3
"""
Live test against MS108EUP switch.

This script tests the full py-netgear-plus library against your actual switch.

Usage:
    cd ~/Development/py-netgear-plus/pages/MS108EUP
    python test_live.py --ip 192.168.1.5 --password YOUR_PASSWORD
"""

import argparse
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from py_netgear_plus import NetgearSwitchConnector


def test_switch(ip: str, password: str):
    """Run full test against the switch."""

    print(f"\n{'='*60}")
    print(f"Testing MS108EUP at {ip}")
    print(f"{'='*60}\n")

    # Create connector
    print("[1/4] Creating connector...")
    try:
        api = NetgearSwitchConnector(ip, password)
        print("       ✓ Connector created")
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Auto-detect model
    print("\n[2/4] Auto-detecting model...")
    try:
        api.autodetect_model()
        model_name = api.switch_model.MODEL_NAME if api.switch_model else "None"
        print(f"       ✓ Detected: {model_name}")

        if model_name != "MS108EUP":
            print(f"       ⚠ WARNING: Expected MS108EUP but got {model_name}")
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Login to get Gambit token
    print("\n[3/5] Logging in...")
    try:
        logged_in = api.get_login_cookie()
        if logged_in:
            print("       ✓ Login successful")
        else:
            print("       ✗ Login failed")
            return False
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Get switch info
    print("\n[4/5] Fetching switch info...")
    try:
        info = api.get_switch_infos()
        print("       ✓ Switch info retrieved")
    except Exception as e:
        print(f"       ✗ ERROR: {e}")
        return False

    # Display results
    print("\n[5/5] Results:")
    print(f"\n{'='*60}")
    print("SWITCH INFORMATION")
    print(f"{'='*60}\n")

    # Basic info
    basic_keys = ["switch_ip", "switch_name", "switch_serial_number",
                  "switch_firmware", "switch_bootloader", "led_status"]
    print("Basic Info:")
    for key in basic_keys:
        if key in info:
            print(f"  {key}: {info[key]}")

    # Port status
    print("\nPort Status:")
    for port in range(1, 9):
        status = info.get(f"port_{port}_status", "?")
        speed = info.get(f"port_{port}_connection_speed", "?")
        print(f"  Port {port}: {status} ({speed} Mbps)")

    # PoE status
    print("\nPoE Status:")
    for port in range(1, 9):
        poe_active = info.get(f"port_{port}_poe_power_active", "?")
        poe_power = info.get(f"port_{port}_poe_output_power", "?")
        print(f"  Port {port}: {poe_active} ({poe_power}W)")

    # Traffic (if available)
    print("\nTraffic (cumulative):")
    for port in range(1, 9):
        rx = info.get(f"port_{port}_sum_rx_mbytes", 0)
        tx = info.get(f"port_{port}_sum_tx_mbytes", 0)
        if rx > 0 or tx > 0:
            print(f"  Port {port}: RX {rx:.2f} MB, TX {tx:.2f} MB")

    print(f"\n{'='*60}")
    print("✓ All tests passed!")
    print(f"{'='*60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Test py-netgear-plus against your MS108EUP switch"
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="Switch IP address"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Switch admin password"
    )

    args = parser.parse_args()

    success = test_switch(args.ip, args.password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
