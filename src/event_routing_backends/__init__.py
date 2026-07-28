"""
Various backends for receiving edX LMS events..
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("edx-event-routing-backends")
except PackageNotFoundError:
    __version__ = "0.0.0"
