# MS108EUP Switch Support Implementation

This directory contains test data for the Netgear MS108EUP (Multi-Gig 8-Port PoE++ Ultra60) switch.

## Step-by-Step Implementation Guide

### Prerequisites

1. A Netgear MS108EUP switch accessible on your network
2. The switch's admin password
3. Python 3.9+ installed
4. The `requests` library (`pip install requests`)

---

## Step 1: Set Up Development Environment

```bash
# Navigate to the py-netgear-plus repo
cd ~/Development/py-netgear-plus

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install the package in development mode with test dependencies
pip install -e ".[dev]"

# Or if that fails, install manually:
pip install -e .
pip install pytest pytest-asyncio requests
```

---

## Step 2: Capture HTML Data from Your Switch

The capture script will connect to your switch and save all the HTML responses needed for testing.

```bash
# Navigate to the MS108EUP pages directory
cd ~/Development/py-netgear-plus/pages/MS108EUP

# Run the capture script for sample 0 (first snapshot)
python capture_switch_data.py --ip YOUR_SWITCH_IP --password YOUR_PASSWORD --sample 0

# Example:
python capture_switch_data.py --ip 192.168.1.5 --password mypassword123 --sample 0
```

**Wait 30-60 seconds**, then run the second capture:

```bash
# Run the capture script for sample 1 (second snapshot)
python capture_switch_data.py --ip YOUR_SWITCH_IP --password YOUR_PASSWORD --sample 1
```

This creates two snapshots needed for traffic rate calculations.

---

## Step 3: Verify Captured Files

After running both captures, you should have this structure:

```
pages/MS108EUP/
├── README.md              (this file)
├── capture_switch_data.py (capture script)
├── unauthenticated.html   (login page)
├── 0/
│   ├── homepage.html
│   ├── dashboard.html
│   ├── interface_stats.html
│   ├── poePortConf.html
│   ├── poePortStatus.html
│   └── getPortRate.html (optional)
└── 1/
    ├── homepage.html
    ├── dashboard.html
    ├── interface_stats.html
    ├── poePortConf.html
    ├── poePortStatus.html
    └── getPortRate.html (optional)
```

Check file sizes - they should not be empty:
```bash
ls -la 0/ 1/
```

---

## Step 4: Create Expected Output JSON

Create `switch_infos.json` files that define what the parsed output should look like.

```bash
# Create a template (you'll need to fill in actual values)
cd ~/Development/py-netgear-plus/pages/MS108EUP
```

Create `0/switch_infos.json` with your switch's actual data:

```json
{
  "switch_ip": "192.168.1.5",
  "switch_name": "MS108EUP",
  "switch_serial_number": "YOUR_SERIAL",
  "switch_bootloader": "unknown",
  "switch_firmware": "1.0.2.7",
  "port_1_status": "on",
  "port_1_modus_speed": true,
  "port_1_connection_speed": 1000,
  "port_2_status": "off",
  "port_2_modus_speed": true,
  "port_2_connection_speed": 0,
  ... (continue for all 8 ports)
}
```

---

## Step 5: Run Tests

```bash
# Navigate to repo root
cd ~/Development/py-netgear-plus

# Run all tests
pytest -v

# Run only MS108EUP-related tests (once they exist)
pytest -v -k "MS108EUP"

# Run tests with more detail on failures
pytest -v --tb=long
```

---

## Step 6: Troubleshoot Parser Issues

If tests fail, the HTML structure may differ from what the parser expects.

### Debug the Parser

Create a test script `test_parser.py`:

```python
#!/usr/bin/env python3
"""Test MS108EUP parser against captured HTML."""

from pathlib import Path
from py_netgear_plus.parsers import MS108EUP

# Load captured HTML
pages_dir = Path(__file__).parent / "0"

parser = MS108EUP()

# Test switch metadata parsing
print("Testing parse_switch_metadata...")
with open(pages_dir / "dashboard.html") as f:
    class FakeResponse:
        content = f.read().encode()
    try:
        result = parser.parse_switch_metadata(FakeResponse())
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Test port status parsing
print("\nTesting parse_port_status...")
with open(pages_dir / "dashboard.html") as f:
    class FakeResponse:
        content = f.read().encode()
    try:
        result = parser.parse_port_status(FakeResponse(), ports=8)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ERROR: {e}")

# Test port statistics parsing
print("\nTesting parse_port_statistics...")
with open(pages_dir / "interface_stats.html") as f:
    class FakeResponse:
        content = f.read().encode()
    try:
        result = parser.parse_port_statistics(FakeResponse(), ports=8)
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  ERROR: {e}")

print("\nDone!")
```

Run it:
```bash
python test_parser.py
```

If parsing fails, examine the HTML structure and adjust the parser methods in:
`~/Development/py-netgear-plus/src/py_netgear_plus/parsers.py`

---

## Step 7: Test with Actual Switch (Live Test)

Once parsing works, test against your real switch:

```bash
cd ~/Development/py-netgear-plus
```

Create `test_live.py`:

```python
#!/usr/bin/env python3
"""Live test against MS108EUP switch."""

from py_netgear_plus import NetgearSwitchConnector

SWITCH_IP = "192.168.1.5"  # Your switch IP
PASSWORD = "your_password"  # Your switch password

print(f"Connecting to {SWITCH_IP}...")
api = NetgearSwitchConnector(SWITCH_IP, PASSWORD)

print("Auto-detecting model...")
api.autodetect_model()
print(f"Detected model: {api.switch_model}")

print("\nFetching switch info...")
info = api.get_switch_infos()

print("\n--- Switch Info ---")
for key, value in sorted(info.items()):
    print(f"  {key}: {value}")
```

Run it:
```bash
python test_live.py
```

---

## Step 8: Test with Home Assistant

Once py-netgear-plus works:

### Option A: Install from Local Path

Edit `~/Development/ha-netgear-plus/custom_components/netgear_plus/manifest.json`:

```json
{
  "requirements": [
    "py-netgear-plus @ file:///path/to/py-netgear-plus"
  ]
}
```

### Option B: Use pip install

```bash
# Install your local py-netgear-plus globally
pip install ~/Development/py-netgear-plus
```

### Copy Integration to Home Assistant

```bash
# Copy to your Home Assistant config
cp -r ~/Development/ha-netgear-plus/custom_components/netgear_plus \
      /path/to/homeassistant/config/custom_components/

# Restart Home Assistant
```

---

## Step 9: Submit Pull Requests

Once everything works:

### For py-netgear-plus:

1. Fork https://github.com/foxey/py-netgear-plus on GitHub
2. Create a branch: `git checkout -b add-ms108eup-support`
3. Commit your changes
4. Push and create PR

### Files to include in PR:
- `src/py_netgear_plus/models.py` (MS108EUP class)
- `src/py_netgear_plus/parsers.py` (MS108EUP parser)
- `pages/MS108EUP/` (test data directory)
- Update `README.md` (add MS108EUP to supported models)

---

## Troubleshooting

### "Could not find 'rand' value"
The login page HTML structure may be different. Check `unauthenticated.html` and look for the rand input field.

### "Login failed - no gambitCookie"
- Check password is correct
- Check `debug_login_response.html` for error messages
- The switch may use a different authentication method

### Parser errors
- Examine the captured HTML files
- Compare with similar models (GS316EPP has similar structure)
- Adjust XPath queries in parsers.py

### Connection refused
- Check switch IP is correct
- Ensure switch web interface is enabled
- Try accessing http://YOUR_SWITCH_IP in a browser
