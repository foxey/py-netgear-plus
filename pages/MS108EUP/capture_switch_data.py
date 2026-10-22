#!/usr/bin/env python3
"""
MS108EUP HTML Capture Script

This script captures HTML responses from your MS108EUP switch for testing.
Run this script twice with a 30-60 second delay to capture both sample sets.

Usage:
    # First capture (sample 0)
    python capture_switch_data.py --ip 192.168.1.5 --password YOUR_PASSWORD --sample 0

    # Wait 30-60 seconds, then run again for sample 1
    python capture_switch_data.py --ip 192.168.1.5 --password YOUR_PASSWORD --sample 1
"""

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests


def md5_hash(text: str) -> str:
    """Generate MD5 hash of text."""
    return hashlib.md5(text.encode()).hexdigest()


def merge(str1: str, str2: str) -> str:
    """Merge two strings by alternating characters from each string."""
    result = ""
    arr1 = list(str1) if str1 else []
    arr2 = list(str2) if str2 else []
    index1 = 0
    index2 = 0
    while (index1 < len(arr1)) or (index2 < len(arr2)):
        if index1 < len(arr1):
            result += arr1[index1]
            index1 += 1
        if index2 < len(arr2):
            result += arr2[index2]
            index2 += 1
    return result


def merge_hash(password: str, rand: str) -> str:
    """Return MD5 hash of merged password and rand strings."""
    return md5_hash(merge(password, rand))


def extract_rand(html: str) -> Optional[str]:
    """Extract rand value from login page HTML."""
    match = re.search(r'<input[^>]+id=["\']rand["\'][^>]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    match = re.search(r'<input[^>]+value=["\']([^"\']+)["\'][^>]+id=["\']rand["\']', html)
    if match:
        return match.group(1)
    return None


def extract_gambit(html: str) -> Optional[str]:
    """Extract Gambit token from HTML response."""
    match = re.search(r'<input[^>]+name=["\']Gambit["\'][^>]+value=["\']([^"\']+)["\']', html)
    if match:
        return match.group(1)
    match = re.search(r'<input[^>]+value=["\']([^"\']+)["\'][^>]+name=["\']Gambit["\']', html)
    if match:
        return match.group(1)
    return None


def capture_switch_data(ip: str, password: str, sample_dir: Path) -> bool:
    """Capture all HTML pages from the switch."""

    session = requests.Session()
    base_url = f"http://{ip}"

    print(f"\n{'='*60}")
    print(f"Capturing MS108EUP data from {ip}")
    print(f"Saving to: {sample_dir}")
    print(f"{'='*60}\n")

    # Step 1: Get login page
    print("[1/7] Fetching login page...")
    try:
        login_resp = session.get(f"{base_url}/wmi/login", timeout=10)
        login_resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Could not connect to switch at {ip}")
        print(f"       {e}")
        return False

    # Save unauthenticated login page (only needed once)
    unauth_file = sample_dir.parent / "unauthenticated.html"
    if not unauth_file.exists():
        unauth_file.write_text(login_resp.text)
        print(f"       Saved: unauthenticated.html")

    # Extract rand value
    rand_value = extract_rand(login_resp.text)
    if not rand_value:
        print("ERROR: Could not find 'rand' value in login page")
        print("       Please check if the login page HTML structure is different")
        return False
    print(f"       Found rand value: {rand_value}")

    # Step 2: Login
    print("\n[2/7] Logging in...")
    # Use merge_hash: interleave password and rand characters, then MD5
    password_hash = merge_hash(password, rand_value)
    print(f"       Password hash: {password_hash[:16]}...")

    login_data = {"LoginPassword": password_hash}

    try:
        # Try posting to /redirect.html first
        login_post_resp = session.post(
            f"{base_url}/redirect.html",
            data=login_data,
            timeout=10,
            allow_redirects=True
        )
    except requests.RequestException as e:
        print(f"ERROR: Login failed: {e}")
        return False

    # Check for gambit cookie
    gambit_cookie = session.cookies.get("gambitCookie")
    if not gambit_cookie:
        # Try to extract from response HTML
        gambit_cookie = extract_gambit(login_post_resp.text)

    if not gambit_cookie:
        print("ERROR: Login may have failed - no gambitCookie found")
        print("       Check if password is correct")
        print(f"       Response status: {login_post_resp.status_code}")
        # Save the response for debugging
        debug_file = sample_dir / "debug_login_response.html"
        debug_file.write_text(login_post_resp.text)
        print(f"       Saved response to: {debug_file}")
        return False

    print(f"       Login successful! Gambit: {gambit_cookie[:20]}...")

    # Save homepage response
    homepage_file = sample_dir / "homepage.html"
    homepage_file.write_text(login_post_resp.text)
    print(f"       Saved: homepage.html")

    # Step 3: Fetch dashboard (switch info + port status)
    print("\n[3/7] Fetching dashboard (switch info & port status)...")
    try:
        dashboard_resp = session.get(
            f"{base_url}/iss/specific/dashboard.html",
            params={"Gambit": gambit_cookie},
            timeout=10
        )
        dashboard_file = sample_dir / "dashboard.html"
        dashboard_file.write_text(dashboard_resp.text)
        print(f"       Saved: dashboard.html ({len(dashboard_resp.text)} bytes)")
    except requests.RequestException as e:
        print(f"WARNING: Could not fetch dashboard: {e}")

    # Step 4: Fetch interface statistics
    print("\n[4/7] Fetching port statistics...")
    try:
        stats_resp = session.get(
            f"{base_url}/iss/specific/interface_stats.html",
            params={"Gambit": gambit_cookie},
            timeout=10
        )
        stats_file = sample_dir / "interface_stats.html"
        stats_file.write_text(stats_resp.text)
        print(f"       Saved: interface_stats.html ({len(stats_resp.text)} bytes)")
    except requests.RequestException as e:
        print(f"WARNING: Could not fetch interface stats: {e}")

    # Step 5: Fetch PoE port configuration
    print("\n[5/7] Fetching PoE port configuration...")
    try:
        poe_conf_resp = session.get(
            f"{base_url}/iss/specific/poePortConf.html",
            params={"Gambit": gambit_cookie},
            timeout=10
        )
        poe_conf_file = sample_dir / "poePortConf.html"
        poe_conf_file.write_text(poe_conf_resp.text)
        print(f"       Saved: poePortConf.html ({len(poe_conf_resp.text)} bytes)")
    except requests.RequestException as e:
        print(f"WARNING: Could not fetch PoE config: {e}")

    # Step 6: Fetch PoE port status
    print("\n[6/7] Fetching PoE port status...")
    try:
        poe_status_resp = session.get(
            f"{base_url}/iss/specific/poePortStatus.html",
            params={"Gambit": gambit_cookie, "GetData": "TRUE"},
            timeout=10
        )
        poe_status_file = sample_dir / "poePortStatus.html"
        poe_status_file.write_text(poe_status_resp.text)
        print(f"       Saved: poePortStatus.html ({len(poe_status_resp.text)} bytes)")
    except requests.RequestException as e:
        print(f"WARNING: Could not fetch PoE status: {e}")

    # Step 7: Try fetching the unique port rate data (bonus)
    print("\n[7/7] Fetching port rate data (optional)...")
    try:
        rate_resp = session.post(
            f"{base_url}/iss/specific/getPortRate.html",
            data={
                "gambit": gambit_cookie,
                "transtype": "download",
                "requesttype": "fiveM"
            },
            timeout=10
        )
        rate_file = sample_dir / "getPortRate.html"
        rate_file.write_text(rate_resp.text)
        print(f"       Saved: getPortRate.html ({len(rate_resp.text)} bytes)")
    except requests.RequestException as e:
        print(f"NOTE: Could not fetch port rate data: {e}")
        print("      (This endpoint may not exist on all firmware versions)")

    print(f"\n{'='*60}")
    print("Capture complete!")
    print(f"Files saved to: {sample_dir}")
    print(f"{'='*60}\n")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Capture HTML data from MS108EUP switch for testing"
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="Switch IP address (e.g., 192.168.1.5)"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Switch admin password"
    )
    parser.add_argument(
        "--sample",
        type=int,
        choices=[0, 1],
        required=True,
        help="Sample number (0 for first capture, 1 for second)"
    )

    args = parser.parse_args()

    # Determine output directory
    script_dir = Path(__file__).parent
    sample_dir = script_dir / str(args.sample)
    sample_dir.mkdir(exist_ok=True)

    success = capture_switch_data(args.ip, args.password, sample_dir)

    if success and args.sample == 0:
        print("\n" + "="*60)
        print("NEXT STEP:")
        print("Wait 30-60 seconds, then run this command for sample 1:")
        print(f"\n  python {__file__} --ip {args.ip} --password YOUR_PASSWORD --sample 1")
        print("\nThis captures a second snapshot for traffic rate calculations.")
        print("="*60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
