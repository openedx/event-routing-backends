"""
Exceptions related to Caliper transformation
"""


class NoTransformerImplemented(Exception):
    """
    Raise this exception when there is no transformer implemented
    for an event.
    """
