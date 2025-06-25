"""
startpageapi
~~~~~~~~~~~~

A Python wrapper for the Startpage Search API.

:copyright: (c) 2023 by deepnor
:license: MIT, see LICENSE for more details.
"""

__author__ = "deepnor"
__license__ = "MIT"
__version__ = "1.1.0"


from .client import StartpageAPI
from .exceptions import (
    StartpageError,
    StartpageHTTPError,
    StartpageParseError,
    StartpageRateLimitError,
)


__all__ = [
    "StartpageAPI",
    "StartpageError",
    "StartpageHTTPError",
    "StartpageParseError",
    "StartpageRateLimitError",
]
