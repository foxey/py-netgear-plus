"""Unit tests for the py_netgear_plus ngp_cli module."""

import argparse
from unittest.mock import Mock, patch

import pytest
from py_netgear_plus import InvalidPoEPortError
from py_netgear_plus.ngp_cli import _poe_status, _print_table, poe_command


def _poe_args(
    action: str | None = None, port: int = 1, *, json: bool = False
) -> argparse.Namespace:
    return argparse.Namespace(poe_action=action, port=port, json=json)


def _connector(poe_ports: list[int]) -> Mock:
    connector = Mock()
    connector.switch_model.POE_PORTS = poe_ports
    return connector


def test_poe_command_missing_subcommand() -> None:
    """Poe with no subcommand fails without touching the connector."""
    connector = _connector([1, 2])
    assert poe_command(connector, _poe_args(None)) is False
    connector.autodetect_model.assert_not_called()


def test_poe_command_not_logged_in() -> None:
    """Poe fails cleanly when not logged in."""
    connector = _connector([1, 2])
    with patch("py_netgear_plus.ngp_cli.load_cookie", return_value=False):
        assert poe_command(connector, _poe_args("status")) is False
    connector.autodetect_model.assert_not_called()


def test_poe_command_rejects_non_poe_model() -> None:
    """Poe status/on/off/cycle refuse to run on a switch without PoE ports."""
    connector = _connector([])
    with patch("py_netgear_plus.ngp_cli.load_cookie", return_value=True):
        assert poe_command(connector, _poe_args("status")) is False
    connector.get_poe_port_infos.assert_not_called()


def test_poe_command_status_calls_get_poe_port_infos() -> None:
    """Poe status fetches and displays per-port PoE info."""
    connector = _connector([1, 2])
    connector.get_poe_port_infos.return_value = {
        1: {
            "power_active": "on",
            "power_delivered": "on",
            "status": "delivering_power",
            "class": 4,
            "voltage": 51,
            "current": 119,
            "output_power": 6.1,
            "temperature": 44,
            "fault": "No Error",
        }
    }
    with patch("py_netgear_plus.ngp_cli.load_cookie", return_value=True):
        assert poe_command(connector, _poe_args("status")) is True
    connector.get_poe_port_infos.assert_called_once()


@pytest.mark.parametrize(
    ("action", "method_name"),
    [
        ("on", "turn_on_poe_port"),
        ("off", "turn_off_poe_port"),
        ("cycle", "power_cycle_poe_port"),
    ],
)
def test_poe_command_on_off_cycle_dispatch(action: str, method_name: str) -> None:
    """Poe on/off/cycle call the matching connector method with the port number."""
    connector = _connector([1, 2])
    getattr(connector, method_name).return_value = True
    with patch("py_netgear_plus.ngp_cli.load_cookie", return_value=True):
        assert poe_command(connector, _poe_args(action, port=2)) is True
    getattr(connector, method_name).assert_called_once_with(2)


def test_poe_command_invalid_port_reports_error() -> None:
    """An InvalidPoEPortError from the connector is reported, not raised."""
    connector = _connector([1, 2])
    connector.turn_on_poe_port.side_effect = InvalidPoEPortError("bad port")
    with patch("py_netgear_plus.ngp_cli.load_cookie", return_value=True):
        assert poe_command(connector, _poe_args("on", port=99)) is False


def test_poe_status_json_output(capsys: pytest.CaptureFixture) -> None:
    """Poe status --json prints the raw dict as JSON."""
    connector = Mock()
    connector.get_poe_port_infos.return_value = {1: {"status": "delivering_power"}}
    assert _poe_status(connector, _poe_args("status", json=True)) is True
    out = capsys.readouterr().out
    assert '"status": "delivering_power"' in out


def test_print_table(capsys: pytest.CaptureFixture) -> None:
    """_print_table aligns columns and prints header + rows."""
    _print_table(["port", "status"], [[1, "on"], [2, "off"]])
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("port")
    assert "1" in lines[1]
    assert "on" in lines[1]
