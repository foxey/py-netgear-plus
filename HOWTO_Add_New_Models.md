# How to Add Additional Switch Models to py-netgear-plus

This guide provides step-by-step instructions on how to add support for additional Netgear Plus switch models to the **py-netgear-plus** Python library. The process involves defining a new switch model class, implementing the necessary attributes and methods, and registering the model in the library.

To add a new switch model, you need to update two files:

- **models.py**: This file defines various Netgear Plus switch models. Each model is implemented as a class inheriting from `AutodetectedSwitchModel`, with attributes specifying model-specific details.
- **parsers.py**: This file contains parsing functions used to extract and interpret data from switch responses. If a new model requires unique parsing logic, it should be added here.

---

## 1. Create a New Class for the Switch Model

Each switch model should inherit from `AutodetectedSwitchModel` or from the most similar existing model. Inheriting from a similar model reduces duplication and ensures compatibility with the library's structure. Ensure that `MODEL_NAME` is identical to the class name. Intermediate classes that define logic shared by multiple models should not have a defined `MODEL_NAME` to prevend that `py_netgear_plus.autodetect_model()` finds multiple matching classes.

You can create a new switch model class by following the structure below:

```python
from typing import ClassVar

class GSXYZ(AutodetectedSwitchModel):  # Replace GSXYZ with the actual model name
    """Definition for Netgear GSXYZ model."""

    MODEL_NAME = "GSXYZ"  # Set the actual model name
    PORTS = 8  # Define the number of ports on the switch
    POE_PORTS: ClassVar = [1, 2, 3, 4]  # Define PoE ports (if applicable)
    POE_MAX_POWER_ALL_PORTS = 60  # Define maximum PoE power (if applicable)
    ALLOWED_COOKIE_TYPES: ClassVar = ["SID"]  # Define allowed cookie types

    CHECKS_AND_RESULTS: ClassVar = [
        ("check_login_form_rand", [True]),  # Detection methods
        ("parse_login_title_tag", ["GSXYZ"]),
    ]

    # Mandatory request templates for interacting with the switch
    LOGIN_TEMPLATE: ClassVar = {
        "method": "post",
        "url": "http://{ip}/login.cgi",
        "params": {"password": "_password_hash"},
    }

    SWITCH_INFO_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/switch_info.cgi"},
    ]

    PORT_STATUS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/status.cgi"},
    ]

    PORT_STATISTICS_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/portStatistics.cgi"},
    ]

    LOGOUT_TEMPLATES: ClassVar = [
        {"method": "get", "url": "http://{ip}/logout.cgi"},
    ]
```

The `LOGIN_TEMPLATE`, `SWITCH_INFO_TEMPLATES`, `PORT_STATUS_TEMPLATES`, and `PORT_STATISTICS_TEMPLATES` are mandatory to implement for proper communication with the switch.

Modify the class attributes according to the specific switch model.

---

## 2. Implement Any Additional Model-Specific Methods

If the switch model supports additional functionality (such as PoE settings, LED control, etc.), implement the corresponding methods. For example:

```python
    def get_switch_poe_port_data(self, poe_port: int, state: str) -> dict:
        """Returns data for enabling/disabling a PoE port."""
        return {
            "ACTION": "Apply",
            "portID": poe_port - 1,
            "ADMIN_MODE": 1 if state == "on" else 0,
            "PORT_PRIO": 0,
        }
```

Refer to existing switch models in `models.py` for additional examples.

## 3. Create a Parser Class and Register It in `parsers.py`

Each switch model has its own parser class. If the new model introduces unique parsing logic, create a new parser class in `parsers.py`. Ensure that this parser class inherits from the most similar existing parser class to maintain consistency. The name of the parser class should be identical to the name of the model in `models.py`.

## 4. Add pages responses to the `pages/` folder

The repository contains a collection of page responses used by `pytest` to ensure that no regression problems are introduced during future updates.
The structure of the collection is as follows: `pages/MODEL_NAME/0` and `pages/MODE_NAME/1`. Add a copy of each first successful retrieval from these templates: `AUTODETECT_TEMPLATES`, `LOGIN_TEMPLATE`, `SWITCH_INFO_TEMPLATES`, `PORT_STATUS_TEMPLATES`, and `PORT_STATISTICS_TEMPLATES`to both directories.

Ensure that the response of the login page is the first one sent (most switches redirect to a dashboard page after the initial response) and that the latter three pages are saved using a valid login session (otherwise the only contain a redirect to the login page). Also ensure that for the page retrieved by`PORT_STATISTICS_TEMPLATES`the copy in the`/1`folder is taken 10-60 seconds after the one in the`/0`. The test suite tests if the calculations for the `traffic_rx`and`traffic_tx` speeds are performed correctly.

The pages can be collected with `ngp-cli`:
1. Temporarily change the switch password to `Password1`. Crypted Password will be added to unit tests and tests expect `Password1`
2. login with `ngp-cli --password Password1 login {ip}`
3. collect pages for unit tests `ngp-cli collect`

## 5. Test the New Model and Update Unit Tests

1. Connect the switch to your network.
2. Run the auto-detection feature to verify if the switch is correctly identified.
3. Ensure that all required API endpoints work correctly.
4. If PoE or LED controls are implemented, test them thoroughly.
5. Add unit tests for the new model in the test suite:
   - Locate the unit test file in `tests/test__init__.py` that contains tests for existing switch models.
   - Add the new model to the `MODEL_PARAMETERS` list with appropriate test values (rand, crypted password, and response content).
    
       > example based on GSS108E switch
       >
       > `(GSS108E, "2082437949", "1c0714cfd1c8595db5ba36ceae43b134", "<html></html>")`
       > 
       > |         | Model name        | rand                               | crypted password                             | response content  |
       > | --------| ----------------- | ---------------------------------- | -------------------------------------------- | ----------------- |
       > | example | GSS108E           | 2082437949                         | 1c0714cfd1c8595db5ba36ceae43b134             | \<html\>\</html\> |
       > | where   | switch model name | hidden input element in login form | POST request body from login form submission | ?                 |
   - If the model lacks complete test data, add it to `MODELS_FOR_GET_SWITCH_INFOS` with an appropriate `pytest.mark.xfail` annotation.
   - Run the test suite with `pytest` to confirm all tests pass, and fix any issues as needed.

## 6. Submit a Pull Request

Please share the new model code by creating a pull request in the `py-netgear-plus` repository:

1. Fork the repository.
2. Commit your changes with a descriptive message.
3. Push the changes to your forked repository.
4. Submit a pull request with details about the new model.
