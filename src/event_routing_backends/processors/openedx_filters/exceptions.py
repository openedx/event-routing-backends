"""
Custom processors exceptions thrown by filters.
"""
from openedx_filters.exceptions import OpenEdxFilterException


class InvalidFilterType(OpenEdxFilterException):
    """
    Exception that indicates that the attribute `filter_type` has not been set property.
    """
