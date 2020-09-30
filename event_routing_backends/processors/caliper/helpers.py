"""
Helper utilities for event transformers.
"""
import logging
from datetime import timedelta
from urllib.parse import parse_qs, urlparse

from dateutil.parser import parse
from isodate import duration_isoformat

logger = logging.getLogger(__name__)

UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


def convert_seconds_to_iso(seconds):
    """
    Convert seconds from integer to ISO format.

    Arguments:
        seconds (int): number of seconds

    Returns:
        str
    """
    return duration_isoformat(timedelta(
        seconds=seconds
    ))


def convert_datetime_to_iso(current_datetime):
    """
    Convert provided datetime into UTC format.

    Arguments:
        current_datetime (str):     datetime string

    Returns:
        str
    """

    # convert current_datetime to a datetime object if it is string
    if isinstance(current_datetime, str):
        current_datetime = parse(current_datetime)

    utc_offset = current_datetime.utcoffset()
    utc_datetime = current_datetime - utc_offset

    formatted_datetime = utc_datetime.strftime(UTC_DATETIME_FORMAT)[:-3] + 'Z'

    return formatted_datetime


def get_block_id_from_event_referrer(event):
    """
    Derive and return block id from event referrer

    Arguments:
        event (dict):   event dictionary object.

    Returns:
        str or None
    """
    try:
        parsed = urlparse(event['context']['referer'])
        block_id = parse_qs(parsed.query)['activate_block_id'][0]
        return block_id
    except (KeyError, IndexError):
        logger.error('Could not get block id for event "{}"'.format(event.get('name')))
        return None
