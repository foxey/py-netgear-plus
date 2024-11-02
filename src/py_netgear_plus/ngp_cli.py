#!/bin/env python
"""
Netgear Plus CLI.

A command-line utility to interact with a Netgear switch.
Supports identifying the switch model, logging in, logging out,
and displaying switch status.


Usage:
    python ngp-cli.py <host> [--password <password>] <command>

Commands:
    identify, login, logout, status

Environment Variables:
    NETGEAR_PLUS_PASSWORD: Password for the switch if --password is not provided.
"""

import argparse
import json
import logging
import os
import time
from pathlib import Path
from sys import stderr

from py_netgear_plus import (
    LoginFailedError,
    NetgearSwitchConnector,
    SwitchModelNotDetectedError,
)

COOKIE_FILE = Path.home() / ".netgear_plus_cookie"


def save_cookie(
    connector: NetgearSwitchConnector, filename: Path = COOKIE_FILE
) -> bool:
    """Save the authentication cookie from the NetgearSwitchConnector to a file."""
    with Path(filename).open("w") as f:
        json.dump(
            {
                "cookie_name": connector.cookie_name,
                "cookie_content": connector.cookie_content,
            },
            f,
        )
        return True
    return False


def load_cookie(
    connector: NetgearSwitchConnector, filename: Path = COOKIE_FILE
) -> bool:
    """Load the authentication cookie into the NetgearSwitchConnector from a file."""
    if Path(filename).exists():
        with Path(filename).open("r") as f:
            data = json.load(f)
            connector.cookie_name = data.get("cookie_name")
            connector.cookie_content = data.get("cookie_content")
            return True
    return False


def save_switch_infos(path_prefix: str, switch_infos: dict) -> None:
    """Save switch info to file for debugging."""
    if not Path(path_prefix).exists():
        Path(path_prefix).mkdir(parents=True)
    with Path(f"{path_prefix}/switch_infos.json").open("w") as file:
        json.dump(switch_infos, file, indent=4)


def main() -> None:
    """Parse arguments and execute the corresponding command."""
    parser = argparse.ArgumentParser(description="Netgear Plus CLI")
    parser.add_argument("host", help="Netgear Switch IP address")
    parser.add_argument(
        "--password",
        "-P",
        help="Password for the switch",
        default=os.getenv("NETGEAR_PLUS_PASSWORD"),
    )
    parser.add_argument(
        "--debug",
        "-d",
        help="Enable debug mode",
        action="store_true",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="Be talkative",
        action="store_true",
    )
    parser.add_argument(
        "--filter",
        "-f",
        help="Filter output by the provided string",
        type=str,
        default="",
    )
    parser.add_argument(
        "--json",
        "-j",
        help="Output in JSON format",
        action="store_true",
    )
    parser.add_argument(
        "--path",
        "-p",
        help="Path to save pages and parsed data",
        type=str,
        default="pages",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect a full set of data for testing")
    subparsers.add_parser("identify", help="Identify the switch model")
    subparsers.add_parser("login", help="Login to the switch and save the cookie")
    subparsers.add_parser("logout", help="Logout from the switch and delete the cookie")
    subparsers.add_parser("parse", help="Parse pages and save data to file")
    subparsers.add_parser("save", help="Save pages to file")
    subparsers.add_parser("status", help="Display switch status")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        print("Enabling debug mode.", file=stderr)  # noqa: T201

    if not args.password and args.command not in ["identify", "logout"]:
        print(  # noqa: T201
            "Password is required. Use --password or set"
            " NETGEAR_PLUS_PASSWORD environment variable.",
            file=stderr,
        )
        return

    if args.json and args.filter:
        print("Filtering is not supported with JSON output.", file=stderr)  # noqa: T201
        return

    connector = NetgearSwitchConnector(args.host, args.password)

    command_functions = {
        "collect": collect_command,
        "identify": identify_command,
        "login": login_command,
        "logout": logout_command,
        "parse": parse_command,
        "save": save_command,
        "status": status_command,
    }

    if args.command in command_functions:
        command_functions[args.command](connector, args)
    else:
        print(f"Invalid command: {args.command}\n", file=stderr)  # noqa: T201
        parser.print_help(stderr)


def identify_command(
    connector: NetgearSwitchConnector,
    args: argparse.Namespace,  # noqa: ARG001
) -> bool:
    """Identify the switch model and print the model name."""
    try:
        model = connector.autodetect_model()
    except SwitchModelNotDetectedError:
        print("Failed to detect switch model.", file=stderr)  # noqa: T201
        return False
    else:
        print(f"Switch model: {model.MODEL_NAME}")  # noqa: T201
        return True


def login_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:  # noqa: ARG001
    """Attempt to login and save the cookie."""
    try:
        return connector.get_login_cookie() and save_cookie(connector)
    except LoginFailedError:
        print("Invalid credentials.", file=stderr)  # noqa: T201
        return False


def logout_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:  # noqa: ARG001
    """Logout from the switch and delete the cookie."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    connector.autodetect_model()
    if connector.delete_login_cookie() and Path(COOKIE_FILE).unlink():
        return True
    print("Logout failed.", file=stderr)  # noqa: T201
    return False


def status_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Display switch status."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    if args.verbose:
        print("Getting switch infos...", file=stderr)  # noqa: T201
    switch_infos = connector.get_switch_infos()
    time.sleep(10)
    switch_infos = connector.get_switch_infos()
    if args.json:
        print(json.dumps(switch_infos, indent=4))  # noqa: T201
        return True
    max_key_length = max(len(key) for key in switch_infos)
    for key in sorted(switch_infos.keys()):
        if not args.filter or args.filter in key:
            print(f"{key.ljust(max_key_length)}\t{switch_infos[key]}")  # noqa: T201

    return bool(switch_infos)


def save_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Save pages to file."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    if not Path(args.path).exists():
        Path(args.path).mkdir(parents=True, exist_ok=True)
    if args.verbose:
        print("Saving html pages...", file=stderr)  # noqa: T201
    connector.save_pages(args.path)
    return True


def parse_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Save parsed data to file."""
    if not Path(args.path).exists():
        print(f"Path does not exist: {args.path}", file=stderr)  # noqa: T201
        return False
    if args.verbose:
        print("Parsing html pages...", file=stderr)  # noqa: T201
    connector.turn_on_offline_mode(args.path)
    connector.turn_on_offline_mode(args.path)
    switch_infos = connector.get_switch_infos()
    switch_infos["switch_ip"] = "192.168.0.1"
    save_switch_infos(args.path, switch_infos)
    return True


def collect_command(
    connector: NetgearSwitchConnector, args: argparse.Namespace
) -> bool:
    """Save pages to file."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    model_name = connector.autodetect_model().MODEL_NAME
    n = ["first", "second"]
    for i in range(2):
        if i:
            if args.verbose:
                print("Waiting 10 seconds...", file=stderr)  # noqa: T201
            time.sleep(10)
        path = f"{args.path}/{model_name}/{i}"
        if not Path(path).exists():
            Path(path).mkdir(parents=True, exist_ok=True)
        if args.verbose:
            print(f"Saving {n[i]} set of pages in {path}", file=stderr)  # noqa: T201
        connector.save_pages(path)
    if not connector.switch_model.SUPPORTED:
        print("Switch model not supported, not parsing data.", file=stderr)  # noqa: T201
        return True
    for i in range(2):
        path = f"{args.path}/{model_name}/{i}"
        if args.verbose:
            print(f"Parsing {n[i]} set of pages in {path}", file=stderr)  # noqa: T201
        connector.turn_on_offline_mode(path)
        switch_infos = connector.get_switch_infos()
        switch_infos["switch_ip"] = "192.168.0.1"
        save_switch_infos(path, switch_infos)
    return True


if __name__ == "__main__":
    main()
