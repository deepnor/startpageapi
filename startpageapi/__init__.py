from .client import StartpageAPI
from .exceptions import (
    StartpageError,
    StartpageHTTPError,
    StartpageParseError,
    StartpageRateLimitError
)

__version__ = "1.0.0"
__author__ = "deepnor"
__license__ = "MIT"

__all__ = [
    "StartpageAPI",
    "StartpageError",
    "StartpageHTTPError", 
    "StartpageParseError",
    "StartpageRateLimitError"
]
