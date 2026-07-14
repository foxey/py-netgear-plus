"""HTML page retrieval classes."""

import json
import logging
import re
from contextlib import suppress
from pathlib import Path
from typing import Any, Iterator

import requests
import requests.cookies
from lxml import html
from requests import Response

from py_netgear_plus.models import (
    MODELS,
    AutodetectedSwitchModel,
    InvalidCryptFunctionError,
    SwitchModelNotDetectedError,
)
from py_netgear_plus.netgear_crypt import hex_hmac_md5, merge_hash

DEFAULT_PAGE = "index.htm"
URL_REQUEST_TIMEOUT = 15
status_code_ok = requests.codes.ok
status_code_not_found = requests.codes.not_found
status_code_no_response = requests.codes.no_response
status_code_una