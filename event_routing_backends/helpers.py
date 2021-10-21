"""
Helper utilities for event transformers.
"""
import logging
from datetime import timedelta
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from dateutil.parser import parse
from django.conf import settings
from django.contrib.auth import get_user_model
from isodate import duration_isoformat
# Imported from edx-platform
# pylint: disable=import-error
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.api import get_course_overviews
from openedx.core.djangoapps.external_user_ids.models import ExternalId, ExternalIdType

logger = logging.getLogger(__name__)
User = get_user_model()

UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


def get_anonymous_user_id(username_or_id):
    """
    Generate anonymous user id.

    Generate anonymous id for student.
    In case of anonymous user, return random uuid.

    Arguments:
        username_or_id (str):     username for the learner

    Returns:
        str
    """
    user = user_id = username = None
    if username_or_id:
        try:
            user_id = int(username_or_id)
        except ValueError:
            username = username_or_id

    if username:
        user = User.objects.filter(username=username).first()
    elif user_id:
        user = User.objects.filter(id=user_id).first()

    if not user:
        logger.info('User with username "%s" does not exist. '
                    'Cannot generate anonymous ID', username_or_id)

        anonymous_id = str(uuid4())
    else:
        type_name = ExternalIdType.LTI
        external_id, _ = ExternalId.add_new_user_id(user, type_name)
        if not external_id:
            raise ValueError("External ID type: %s does not exist" % type_name)

        anonymous_id = str(external_id.external_user_id)

    return anonymous_id


def get_course_from_id(course_id):
    """
    Get Course object using the `course_id`.

    Arguments:
        course_id (str) :   ID of the course

    Returns:
        Course
    """
    course_key = CourseKey.from_string(course_id)
    return get_course_overviews([course_key])[0]


def convert_seconds_to_iso(seconds):
    """
    Convert seconds from integer to ISO format.

    Arguments:
        seconds (int): number of seconds

    Returns:
        str
    """
    if seconds is None:
        return None
    return duration_isoformat(timedelta(
        seconds=seconds
    ))


def convert_seconds_to_float(seconds):
    """
    Convert seconds from integer to Float format.

    Arguments:
        seconds(str) : number of seconds

    Returns:
        float
    """
    if seconds is None or (seconds != 0 and not seconds):
        return None
    else:
        return float("{0:.3f}".format(float(seconds)))


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


def get_block_id_from_event_referrer(referrer):
    """
    Derive and return block id from event referrer.

    Arguments:
        referrer (str):   referrer string.

    Returns:
        str or None
    """
    if referrer is not None:
        parsed = urlparse(referrer)
        block_id = parse_qs(parsed.query)['activate_block_id'][0]\
            if 'activate_block_id' in parse_qs(parsed.query) and parse_qs(parsed.query)['activate_block_id'][0] \
            else None

    else:
        block_id = None

    return block_id


def get_block_id_from_event_data(data, course_id):
    """
    Derive and return block id from event data.

    Arguments:
        data (str):   data string.
        course_id       (str) : course key string

    Returns:
        str or None
    """
    if data is not None and course_id is not None:
        data_array = data.split('_')
        course_id_array = course_id.split(':')
        block_id = "block-v1:{}+type@problem+block@{}".format(course_id_array[1], data_array[1]) \
            if len(data_array) > 1 and len(course_id_array) > 1 else None
    else:
        block_id = None

    return block_id


def get_problem_block_id(referrer, data, course_id):
    """
    Derive and return block id from event data.

    Arguments:
        referrer (str):   referrer string.
        data (str):   data string.
        course_id       (str) : course key string

    Returns:
        str or None
    """
    block_id = get_block_id_from_event_referrer(referrer)
    if block_id is None:
        block_id = get_block_id_from_event_data(
            data,
            course_id
        )

    return block_id


def make_video_block_id(video_id, course_id, video_block_name='video', block_version='block-v1'):
    """
    Return formatted video block id for provided video and course.

    Arguments:
        video_id        (str) : id for the video object
        course_id       (str) : course key string
        video_block_name(str) : video block prefix to generate video id
        block_version   (str) : xBlock version

    Returns:
        str
    """
    course_id_array = course_id.split(':')
    return '{block_version}:{course_id}+type@{video_block_name}+block@{video_id}'.format(
        block_version=block_version,
        course_id=course_id_array[1],
        video_block_name=video_block_name,
        video_id=video_id
    )


def backend_cache_ttl():
    """
    Return cache time out.

    Returns:
        int
    """
    return getattr(settings, 'EVENT_TRACKING_BACKENDS_CACHE_TTL', 600)


def get_business_critical_events():
    """
    Return list of business critical events.

    Returns:
        list
    """
    return getattr(settings, 'EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS', [
        'edx.course.enrollment.activated',
        'edx.course.enrollment.deactivated',
        'edx.course.grade.passed.first_time'
    ])
