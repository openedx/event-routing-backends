"""
Various backends for receiving edX LMS events..
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_version

try:
    __version__ = get_version("edx-event-routing-backends")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"
