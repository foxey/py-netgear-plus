#!/usr/bin/env python3
"""
Debug login process for MS108EUP.

Usage:
    python debug_login.py --ip 192.168.1.5 --password YOUR_PASSWORD
"""

import argparse
import hashlib
import re
import sys

import requests


def merge(str1: str, str2: str) -> str:
    """Merge two strings by alternating characters."""
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


def md5_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def merge_hash(password: str, rand: str) -> str:
    return md5_hash(merge(password, rand))


def debug_login(ip: str, password: str) -> bool:
    """Debug the login process."""
    session = requests.Session()

    print("=" * 60)
    print("Debug Login for MS108EUP")
    print("=" * 60)

    # Step 1: Get login page
    print("\n[1] Fetching login page...")
    try:
        resp = session.get(f"http://{ip}/wmi/login", timeout=10)
        print(f"    Status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"    ERROR: Could not connect to {ip}")
        print(f"    {e}")
        return False

    # Extract rand
    match = re.search(r'id=[\'"]rand[\'"][^>]+value=[\'"]([^\'"]+)[\'"]', resp.text)
    if not match:
        match = re.search(r'value=[\'"]([^\'"]+)[\'"][^>]+id=[\'"]rand[\'"]', resp.text)
    if match:
        rand = match.group(1)
        print(f"    Rand: {rand}")
    else:
        print("    ERROR: Could not find rand!")
        return False

    # Step 2: Login
    print("\n[2] Logging in...")
    password_hash = merge_hash(password, rand)
    print(f"    Password hash: {password_hash}")

    login_resp = session.post(
        f"http://{ip}/homepage.html",
        data={"LoginPassword": password_hash},
        allow_redirects=True,
        timeout=10,
    )
    print(f"    Status: {login_resp.status_code}")
    print(f"    Response length: {len(login_resp.text)} bytes")

    # Check for error messages
    if "Invalid Password" in login_resp.text:
        print("    ERROR: Invalid Password!")
        return False
    elif "maximum" in login_resp.text.lower() and "session" in login_resp.text.lower():
        print("    ERROR: Maximum sessions reached!")
        print("\n    SOLUTION: Log out of the switch's web interface,")
        print("    or restart the switch to clear all sessions.")
        return False
    else:
        print("    No obvious error message")

    # Look for Gambit
    match = re.search(r'name=[\'"]Gambit[\'"][^>]+value=[\'"]([^\'"]+)[\'"]', login_resp.text)
    if not match:
        match = re.search(r'value=[\'"]([^\'"]+)[\'"][^>]+name=[\'"]Gambit[\'"]', login_resp.text)

    if match:
        gambit = match.group(1)
        print(f"\n[3] SUCCESS! Found Gambit: {gambit[:30]}...")
    else:
        print("\n[3] FAILED: No Gambit found in response")
        print("\n    First 500 chars of response:")
        print("    " + "-" * 50)
        print(f"    {login_resp.text[:500]}")
        print("    " + "-" * 50)
        return False

    # Check cookies
    print(f"\n[4] Cookies: {dict(session.cookies)}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Debug MS108EUP login process")
    parser.add_argument("--ip", required=True, help="Switch IP address")
    parser.add_argument("--password", required=True, help="Switch password")
    args = parser.parse_args()

    success = debug_login(args.ip, args.password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
