#!/bin/env python
"""
Netgear Plus CLI.

A command-line utility to interact with a Netgear switch. This tool allows users to
perform various operations on a Netgear switch, such as logging in, identifying the
switch model, collecting data, logging out, and checking switch status.

Usage:
    ngp-cli [--password <password>] [options] <command>

Commands:
    login <host>      Log in to the switch and save the cookie for future commands.
    logout            Log out from the switch and delete the saved cookie.
    identify          Identify the switch model.
    status            Display the current status of the switch.
    collect           Collect a full set of data from the switch for testing.
    parse             Parse collected pages and save data to a file.
    save              Save pages retrieved from the switch to a file.
    version           Display the CLI version.
    vlan              Manage VLAN configuration (sub: status/mode/add/edit/
                        remove/pvid/apply).

Options:
    --password, -P    Specify the password for the switch. If not provided,
                        the NETGEAR_PLUS_PASSWORD environment variable is used.
    --debug, -d       Enable debug mode for detailed logs.
    --verbose, -v     Enable verbose mode for detailed outputs.
    --filter, -f      Filter output by a specified string.
    --json, -j        Output results in JSON format.
    --path, -p        Specify the path for saving pages or parsed data
                        (default: "pages").

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
from typing import Any

from py_netgear_plus import (
    LoginFailedError,
    NetgearSwitchConnector,
    SwitchModelNotDetectedError,
)
from py_netgear_plus import (
    __version__ as ngp_version,
)

COOKIE_FILE = Path.home() / ".netgear_plus_cookie"


def save_cookie(
    connector: NetgearSwitchConnector, filename: Path = COOKIE_FILE
) -> bool:
    """Save the authentication cookie and host to a file."""
    with Path(filename).open("w") as f:
        (cookie_name, cookie_content) = connector.get_cookie()
        json.dump(
            {
                "cookie_name": cookie_name,
                "cookie_content": cookie_content,
                "host": connector.host,
            },
            f,
        )
        return True
    return False


def load_cookie(
    connector: NetgearSwitchConnector, filename: Path = COOKIE_FILE
) -> bool:
    """Load the authentication cookie and host from a file."""
    if Path(filename).exists():
        with Path(filename).open("r") as f:
            data = json.load(f)
            connector.set_cookie(data.get("cookie_name"), data.get("cookie_content"))
            connector.host = data.get("host")
            return True
    return False


def get_saved_host() -> str | None:
    """Retrieve the saved host from the cookie file."""
    if Path(COOKIE_FILE).exists():
        with Path(COOKIE_FILE).open("r") as f:
            data = json.load(f)
            return data.get("host")
    return None


def save_switch_infos(path_prefix: str, switch_infos: dict) -> None:
    """Save switch info to file for debugging."""
    if not Path(path_prefix).exists():
        Path(path_prefix).mkdir(parents=True)
    with Path(f"{path_prefix}/switch_infos.json").open("w") as file:
        json.dump(switch_infos, file, indent=4)


def main() -> None:
    """Parse arguments and execute the corresponding command."""
    parser = parse_commandline()
    args = parser.parse_args()

    if args.command == "version":
        version_command()
        return

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        print("Enabling debug mode.", file=stderr)  # noqa: T201

    command_functions = {
        "collect": collect_command,
        "identify": identify_command,
        "login": login_command,
        "logout": logout_command,
        "parse": parse_command,
        "reboot": reboot_command,
        "save": save_command,
        "status": status_command,
        "version": version_command,
        "vlan": vlan_command,
        "port": port_command,
        "network": network_command,
    }

    if args.command in command_functions:
        command_chooser(args, command_functions)

    else:
        if args.command:
            print(f"Invalid command: {args.command}\n", file=stderr)  # noqa: T201
        parser.print_help(stderr)


def parse_commandline() -> argparse.ArgumentParser:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Netgear Plus CLI")
    parser.add_argument(
        "--password",
        "-P",
        help="Password for the switch. "
        "Defaults to NETGEAR_PLUS_PASSWORD environment variable (if set).",
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

    login_parser = subparsers.add_parser(
        "login", help="Login to the switch and save the cookie"
    )
    login_parser.add_argument("host", help="Netgear Switch IP address")

    identify_parser = subparsers.add_parser(
        "identify", help="Identify the switch model"
    )
    identify_parser.add_argument(
        "host", help="Netgear Switch IP address", nargs="?", default=""
    )

    subparsers.add_parser("collect", help="Collect a full set of data for testing")
    subparsers.add_parser("logout", help="Logout from the switch and delete the cookie")
    subparsers.add_parser("parse", help="Parse pages and save data to file")
    subparsers.add_parser("reboot", help="Reboot the switch")
    subparsers.add_parser("save", help="Save pages to file")
    subparsers.add_parser("status", help="Display switch status")
    subparsers.add_parser("version", help="Display CLI version")

    _add_vlan_subparser(subparsers)
    _add_port_subparser(subparsers)
    _add_network_subparser(subparsers)

    return parser


def _add_vlan_subparser(subparsers: argparse._SubParsersAction) -> None:
    vlan_parser = subparsers.add_parser("vlan", help="VLAN management")
    vlan_sub = vlan_parser.add_subparsers(dest="vlan_action")
    vlan_sub.add_parser("status", help="Show VLAN status")
    vlan_mode_parser = vlan_sub.add_parser("mode", help="Set VLAN mode")
    vlan_mode_parser.add_argument(
        "mode",
        choices=["noVlan", "bscPotBsd", "advPotBsd", "bsc8021Q", "adv8021Q"],
    )
    for verb in ("add", "edit"):
        sp = vlan_sub.add_parser(verb, help=f"{verb.capitalize()} a VLAN")
        sp.add_argument("vlan_id", type=int)
        sp.add_argument("name")
        sp.add_argument(
            "ports",
            help=(
                "Port membership string, e.g. 'TUUUUUUE' "
                "(T=Tagged, U=Untagged, E=Excluded)"
            ),
        )
        sp.add_argument("--voice", action="store_true", help="Mark as voice VLAN")
        sp.add_argument("--voice-cos", type=int, default=6)
    vlan_remove_parser = vlan_sub.add_parser("remove", help="Delete a VLAN")
    vlan_remove_parser.add_argument("vlan_id", type=int)
    vlan_pvid_parser = vlan_sub.add_parser("pvid", help="Set port PVID")
    vlan_pvid_parser.add_argument("port", type=int)
    vlan_pvid_parser.add_argument("vlan_id", type=int)
    vlan_apply_parser = vlan_sub.add_parser(
        "apply", help="Apply a VLAN config from a JSON file"
    )
    vlan_apply_parser.add_argument("file")
    vlan_apply_parser.add_argument(
        "--strict",
        action="store_true",
        help="Remove VLANs not listed in the config (except VLAN 1)",
    )


def _add_port_subparser(subparsers: argparse._SubParsersAction) -> None:
    port_parser = subparsers.add_parser("port", help="Port management")
    port_sub = port_parser.add_subparsers(dest="port_action")
    port_sub.add_parser("list", help="Show per-port settings")
    port_rename = port_sub.add_parser("rename", help="Rename a port")
    port_rename.add_argument("port", type=int)
    port_rename.add_argument("name")


def _add_network_subparser(subparsers: argparse._SubParsersAction) -> None:
    net_parser = subparsers.add_parser("network", help="IP/DHCP management")
    net_sub = net_parser.add_subparsers(dest="network_action")
    net_sub.add_parser("show", help="Show IP/DHCP configuration")
    net_set = net_sub.add_parser("set", help="Apply IP/DHCP configuration")
    net_mode = net_set.add_mutually_exclusive_group(required=True)
    net_mode.add_argument("--dhcp", action="store_true", help="Use DHCP")
    net_mode.add_argument(
        "--static",
        nargs=3,
        metavar=("IP", "MASK", "GATEWAY"),
        help="Static IP / subnet mask / gateway",
    )


def command_chooser(
    args: argparse.Namespace, command_functions: dict[str, Any]
) -> None:
    """Choose the appropriate command function based on the command-line arguments."""
    connector = None
    if args.command == "login":
        if not args.password:
            print("Password is required for login.", file=stderr)  # noqa: T201
            return
        connector = NetgearSwitchConnector(args.host, args.password)
    elif args.command == "identify":
        host = args.host or get_saved_host()
        if not host:
            print("Host is required for identify.", file=stderr)  # noqa: T201
            return
        connector = NetgearSwitchConnector(str(host), args.password)
    else:
        saved_host = get_saved_host()
        if not saved_host:
            print("Host not found. Please login first.", file=stderr)  # noqa: T201
            return
        connector = NetgearSwitchConnector(saved_host, args.password)

    try:
        command_functions[args.command](connector, args)
    except LoginFailedError:
        print("Invalid credentials. Please login again.", file=stderr)  # noqa: T201
        if Path.exists(COOKIE_FILE):
            Path(COOKIE_FILE).unlink()


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
    for i in range(2):
        path = f"{args.path}/{model_name}/{i}"
        if args.verbose:
            print(f"Parsing {n[i]} set of pages in {path}", file=stderr)  # noqa: T201
        connector.turn_on_offline_mode(path)
        switch_infos = connector.get_switch_infos()
        switch_infos["switch_ip"] = "192.168.0.1"
        save_switch_infos(path, switch_infos)
    connector.turn_on_online_mode()
    path = f"{args.path}/{model_name}/0"
    if args.verbose:
        print(  # noqa: T201
            f"Logging out to collect autodetect pages.\nSaving in {path}.", file=stderr
        )
    logout_command(connector, args)
    connector.save_autodetect_templates(path)
    return True


def identify_command(
    connector: NetgearSwitchConnector,
    args: argparse.Namespace,
) -> bool:
    """Identify the switch model and print the model name."""
    del args
    try:
        model = connector.autodetect_model()
    except SwitchModelNotDetectedError:
        print("Failed to detect switch model.", file=stderr)  # noqa: T201
        return False
    else:
        print(f"Switch model: {model.MODEL_NAME}")  # noqa: T201
        return True


def login_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Attempt to login and save the cookie."""
    try:
        if connector.get_login_cookie() and save_cookie(connector):
            if args.verbose:
                print("Login successful.", file=stderr)  # noqa: T201
            return True
    except LoginFailedError:
        print("Invalid credentials.", file=stderr)  # noqa: T201
    return False


def logout_command(
    connector: NetgearSwitchConnector,
    args: argparse.Namespace,
) -> bool:
    """Logout from the switch and delete the cookie."""
    has_cookie = load_cookie(connector)
    if Path.exists(COOKIE_FILE):
        if args.verbose:
            print("Deleting cookie file...", file=stderr)  # noqa: T201
        Path(COOKIE_FILE).unlink()
    if not has_cookie:
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    if connector.delete_login_cookie():
        return True
    print("Logout failed.", file=stderr)  # noqa: T201
    return False


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


def status_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Display switch status."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    if args.verbose:
        print("Getting switch infos...", file=stderr)  # noqa: T201
    switch_infos = connector.get_switch_infos()
    if args.json:
        print(json.dumps(switch_infos, indent=4))  # noqa: T201
        return True
    max_key_length = max(len(key) for key in switch_infos)
    for key in sorted(switch_infos.keys()):
        if not args.filter or args.filter in key:
            print(f"{key.ljust(max_key_length)}\t{switch_infos[key]}")  # noqa: T201
    return bool(switch_infos)


def parse_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Save parsed data to file."""
    if not Path(args.path).exists():
        print(f"Path does not exist: {args.path}", file=stderr)  # noqa: T201
        return False
    if args.verbose:
        print("Parsing html pages...", file=stderr)  # noqa: T201
    connector.turn_on_offline_mode(args.path)
    switch_infos = connector.get_switch_infos()
    switch_infos["switch_ip"] = "192.168.0.1"
    save_switch_infos(args.path, switch_infos)
    return True


def reboot_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Save pages to file."""
    if args.verbose:
        print("Rebooting switch...", file=stderr)  # noqa: T201
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    connector.autodetect_model()
    connector._get_switch_metadata()  # noqa: SLF001
    if connector.reboot():
        if Path.exists(COOKIE_FILE):
            if args.verbose:
                print("Reboot successful. Deleting cookie file...", file=stderr)  # noqa: T201
            Path(COOKIE_FILE).unlink()
        return True
    if args.verbose:
        print("Reboot failed.", file=stderr)  # noqa: T201
    return False


def version_command() -> bool:
    """Display CLI version."""
    print(f"Netgear Plus CLI version: {ngp_version}")  # noqa: T201
    return True


def _vlan_prepare(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Load cookie + autodetect + fetch metadata for VLAN actions."""
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    try:
        connector.autodetect_model()
    except SwitchModelNotDetectedError:
        print("Could not autodetect switch model.", file=stderr)  # noqa: T201
        return False
    if not connector.switch_model.has_vlan_support():
        print(  # noqa: T201
            f"VLAN management not supported on {connector.switch_model.MODEL_NAME}.",
            file=stderr,
        )
        return False
    if args.vlan_action != "status":
        connector._get_switch_metadata()  # noqa: SLF001
    return True


def vlan_command(connector: NetgearSwitchConnector, args: argparse.Namespace) -> bool:
    """Dispatch VLAN subcommands."""
    if not args.vlan_action:
        print("vlan: missing subcommand", file=stderr)  # noqa: T201
        return False

    if not _vlan_prepare(connector, args):
        return False

    try:
        return _vlan_dispatch(connector, args)
    except NotImplementedError as exc:
        model = getattr(connector.switch_model, "MODEL_NAME", "<unknown>")
        print(f"VLAN not supported on {model}: {exc}", file=stderr)  # noqa: T201
        return False


def _vlan_dispatch(  # noqa: PLR0911, PLR0912
    connector: NetgearSwitchConnector, args: argparse.Namespace
) -> bool:
    """Run the VLAN subcommand chosen via args.vlan_action."""
    action = args.vlan_action
    if action == "status":
        status = connector.vlan_status()
        if args.json:
            print(json.dumps(status, indent=4, default=str))  # noqa: T201
        else:
            print(f"Mode: {status['mode']}")  # noqa: T201
            print("VLANs:")  # noqa: T201
            for vid, v in status.get("vlans", {}).items():
                print(f"  {vid}: {v.get('name')} members={v.get('members')}")  # noqa: T201
            print("Ports:")  # noqa: T201
            for p, info in status.get("ports", {}).items():
                pretty_vlans = {
                    vid: m.name.capitalize() for vid, m in info.get("vlans", {}).items()
                }
                print(  # noqa: T201
                    f"  {p}: pvid={info.get('pvid')} vlans={pretty_vlans}"
                )
        return True

    if action == "mode":
        return connector.set_vlan_mode(args.mode)

    if action == "add":
        return connector.add_vlan(
            args.vlan_id, args.name, args.ports, args.voice, args.voice_cos
        )

    if action == "edit":
        return connector.edit_vlan(
            args.vlan_id, args.name, args.ports, args.voice, args.voice_cos
        )

    if action == "remove":
        return connector.remove_vlan(args.vlan_id)

    if action == "pvid":
        return connector.set_vlan_pvid(args.port, args.vlan_id)

    if action == "apply":
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {args.file}", file=stderr)  # noqa: T201
            return False
        with path.open() as f:
            cfg = json.load(f)
        # JSON keys are strings; coerce VLAN/port keys to int.
        if "vlans" in cfg:
            cfg["vlans"] = {int(k): v for k, v in cfg["vlans"].items()}
        if "pvids" in cfg:
            cfg["pvids"] = {int(k): int(v) for k, v in cfg["pvids"].items()}
        summary = connector.apply_vlan_config(cfg, strict=args.strict)
        print(json.dumps(summary, indent=4, default=str))  # noqa: T201
        return True

    print(f"Unknown vlan action: {action}", file=stderr)  # noqa: T201
    return False


def port_command(  # noqa: PLR0911
    connector: NetgearSwitchConnector, args: argparse.Namespace
) -> bool:
    """Dispatch port subcommands."""
    if not args.port_action:
        print("port: missing subcommand", file=stderr)  # noqa: T201
        return False
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    try:
        connector.autodetect_model()
    except SwitchModelNotDetectedError:
        print("Could not autodetect switch model.", file=stderr)  # noqa: T201
        return False
    if not connector.switch_model.has_port_naming():
        print(  # noqa: T201
            f"Port naming not supported on {connector.switch_model.MODEL_NAME}.",
            file=stderr,
        )
        return False
    connector._get_switch_metadata()  # noqa: SLF001
    try:
        if args.port_action == "list":
            settings = connector.get_port_settings()
            if args.json:
                print(json.dumps(settings, indent=4, default=str))  # noqa: T201
            else:
                for p, s in settings.items():
                    print(  # noqa: T201
                        f"  {p}: name='{s['name']}' speed={s['speed']} "
                        f"ingress={s['ingress_rate']} egress={s['egress_rate']} "
                        f"flow_ctrl={s['flow_control']}"
                    )
            return True
        if args.port_action == "rename":
            return connector.set_port_name(args.port, args.name)
    except NotImplementedError as exc:
        model = connector.switch_model.MODEL_NAME
        print(f"Port op not supported on {model}: {exc}", file=stderr)  # noqa: T201
        return False
    print(f"Unknown port action: {args.port_action}", file=stderr)  # noqa: T201
    return False


def network_command(  # noqa: PLR0911, PLR0912
    connector: NetgearSwitchConnector, args: argparse.Namespace
) -> bool:
    """Dispatch network subcommands."""
    if not args.network_action:
        print("network: missing subcommand", file=stderr)  # noqa: T201
        return False
    if not load_cookie(connector):
        print("Not logged in.", file=stderr)  # noqa: T201
        return False
    try:
        connector.autodetect_model()
    except SwitchModelNotDetectedError:
        print("Could not autodetect switch model.", file=stderr)  # noqa: T201
        return False
    if not connector.switch_model.has_ip_config():
        print(  # noqa: T201
            f"Network config not supported on {connector.switch_model.MODEL_NAME}.",
            file=stderr,
        )
        return False
    if args.network_action == "set":
        connector._get_switch_metadata()  # noqa: SLF001
    try:
        if args.network_action == "show":
            cfg = connector.get_ip_config()
            if args.json:
                print(json.dumps(cfg, indent=4))  # noqa: T201
            else:
                mode = "DHCP" if cfg["dhcp"] else "Static"
                print(  # noqa: T201
                    f"mode={mode} ip={cfg['ip_address']} "
                    f"mask={cfg['subnet_mask']} gw={cfg['gateway']}"
                )
            return True
        if args.network_action == "set":
            target_ip = None if args.dhcp else args.static[0]
            if args.dhcp:
                result = connector.set_ip_config(dhcp=True)
            else:
                ip, mask, gw = args.static
                result = connector.set_ip_config(
                    dhcp=False,
                    ip_address=ip,
                    subnet_mask=mask,
                    gateway=gw,
                )
            current_host = connector.host
            if target_ip and target_ip != current_host:
                print(  # noqa: T201
                    f"Note: switch IP changed to {target_ip}. The current "
                    f"TCP session was torn down so the result above may "
                    f"read False even on success. Run "
                    f"`ngp-cli login {target_ip}` to re-establish access.",
                    file=stderr,
                )
            elif args.dhcp:
                print(  # noqa: T201
                    "Note: DHCP enabled. If the lease yields a different "
                    "IP, the current session is torn down; ping the new "
                    "address and `ngp-cli login <new_ip>` to reconnect.",
                    file=stderr,
                )
            return result
    except NotImplementedError as exc:
        print(  # noqa: T201
            f"Network op not supported on {connector.switch_model.MODEL_NAME}: {exc}",
            file=stderr,
        )
        return False
    print(  # noqa: T201
        f"Unknown network action: {args.network_action}", file=stderr
    )
    return False


if __name__ == "__main__":
    main()
