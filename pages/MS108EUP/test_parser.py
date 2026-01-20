#!/usr/bin/env python3
"""
Test MS108EUP parser against captured HTML files.

Run this after capturing HTML data to verify the parser works correctly.

Usage:
    cd ~/Development/py-netgear-plus/pages/MS108EUP
    python test_parser.py
"""

import json
import sys
from pathlib import Path

# Add the src directory to the path so we can import py_netgear_plus
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from py_netgear_plus.parsers import MS108EUP, NetgearPlusPageParserError


class FakeResponse:
    """Fake response object for testing parsers."""

    def __init__(self, content: bytes, status_code: int = 200):
        self.content = content
        self.status_code = status_code


def load_html(file_path: Path) -> FakeResponse | None:
    """Load HTML file and return as FakeResponse."""
    if not file_path.exists():
        return None
    return FakeResponse(file_path.read_bytes())


def test_parser(sample_dir: Path):
    """Test all parser methods against captured HTML."""

    parser = MS108EUP()
    results = {}
    errors = []

    print(f"\n{'='*60}")
    print(f"Testing MS108EUP parser with data from: {sample_dir}")
    print(f"{'='*60}\n")

    # Test 1: parse_switch_metadata
    print("[1/6] Testing parse_switch_metadata...")
    dashboard_file = sample_dir / "dashboard.html"
    if dashboard_file.exists():
        response = load_html(dashboard_file)
        try:
            result = parser.parse_switch_metadata(response)
            results["switch_metadata"] = result
            print(f"       ✓ Success!")
            for key, value in result.items():
                print(f"         {key}: {value}")
        except Exception as e:
            errors.append(("parse_switch_metadata", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {dashboard_file} not found")

    # Test 2: parse_port_status
    print("\n[2/6] Testing parse_port_status...")
    if dashboard_file.exists():
        response = load_html(dashboard_file)
        try:
            result = parser.parse_port_status(response, ports=8)
            results["port_status"] = result
            print(f"       ✓ Success! Found {len(result)} ports")
            for port, status in result.items():
                print(f"         Port {port}: {status}")
        except Exception as e:
            errors.append(("parse_port_status", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {dashboard_file} not found")

    # Test 3: parse_port_statistics
    print("\n[3/6] Testing parse_port_statistics...")
    stats_file = sample_dir / "interface_stats.html"
    if stats_file.exists():
        response = load_html(stats_file)
        try:
            result = parser.parse_port_statistics(response, ports=8)
            results["port_statistics"] = result
            print(f"       ✓ Success!")
            print(f"         RX: {result.get('traffic_rx', [])}")
            print(f"         TX: {result.get('traffic_tx', [])}")
            print(f"         CRC: {result.get('crc_errors', [])}")
        except Exception as e:
            errors.append(("parse_port_statistics", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {stats_file} not found")

    # Test 4: parse_led_status
    print("\n[4/6] Testing parse_led_status...")
    if dashboard_file.exists():
        response = load_html(dashboard_file)
        try:
            result = parser.parse_led_status(response)
            results["led_status"] = result
            print(f"       ✓ Success!")
            print(f"         LED status: {result}")
        except NotImplementedError:
            print(f"       ⚠ Not implemented for this model")
        except Exception as e:
            errors.append(("parse_led_status", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {dashboard_file} not found")

    # Test 5: parse_poe_port_config
    print("\n[5/6] Testing parse_poe_port_config...")
    poe_conf_file = sample_dir / "poePortConf.html"
    if poe_conf_file.exists():
        response = load_html(poe_conf_file)
        try:
            result = parser.parse_poe_port_config(response)
            results["poe_port_config"] = result
            print(f"       ✓ Success!")
            for key, value in result.items():
                print(f"         {key}: {value}")
        except NotImplementedError:
            print(f"       ⚠ Not implemented for this model")
        except Exception as e:
            errors.append(("parse_poe_port_config", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {poe_conf_file} not found")

    # Test 6: parse_poe_port_status
    print("\n[6/6] Testing parse_poe_port_status...")
    poe_status_file = sample_dir / "poePortStatus.html"
    if poe_status_file.exists():
        response = load_html(poe_status_file)
        try:
            result = parser.parse_poe_port_status(response)
            results["poe_port_status"] = result
            print(f"       ✓ Success!")
            for key, value in result.items():
                print(f"         {key}: {value}")
        except NotImplementedError:
            print(f"       ⚠ Not implemented for this model")
        except Exception as e:
            errors.append(("parse_poe_port_status", str(e)))
            print(f"       ✗ ERROR: {e}")
    else:
        print(f"       ⚠ Skipped: {poe_status_file} not found")

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    if errors:
        print(f"\n✗ {len(errors)} parser(s) failed:\n")
        for func_name, error in errors:
            print(f"  - {func_name}: {error}")
        print("\nYou may need to adjust the parser methods in:")
        print("  ~/Development/py-netgear-plus/src/py_netgear_plus/parsers.py")
        print("\nCompare your HTML structure with GS316EPP (similar model):")
        print("  ~/Development/py-netgear-plus/pages/GS316EPP/")
    else:
        print("\n✓ All parsers working correctly!")

    return results, errors


def main():
    script_dir = Path(__file__).parent

    # Check if sample 0 exists
    sample_0 = script_dir / "0"
    if not sample_0.exists() or not any(sample_0.iterdir()):
        print("ERROR: No captured HTML files found in 0/ directory")
        print("\nRun the capture script first:")
        print(f"  python {script_dir}/capture_switch_data.py --ip YOUR_IP --password YOUR_PASSWORD --sample 0")
        sys.exit(1)

    results, errors = test_parser(sample_0)

    # Exit with error code if any parsers failed
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
