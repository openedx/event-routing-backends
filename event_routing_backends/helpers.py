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
from django.urls import reverse
from isodate import duration_isoformat
# Imported from edx-platform
# pylint: disable=import-error
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.api import get_course_overviews
from openedx.core.djangoapps.external_user_ids.models import ExternalId, ExternalIdType

logger = logging.getLogger(__name__)
User = get_user_model()

UTC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


def get_anonymous_user_id_by_username(username):
    """
    Generate anonymous user id.

    Generate anonymous id for student.
    In case of anonymous user, return random uuid.

    Arguments:
        username (str):     username for the learner

    Returns:
        str
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.info('User with username "%s" does not exist. '
                    'Cannot generate anonymous ID', username)

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
        block_id = parse_qs(parsed.query)['activate_block_id'][0]
    else:
        block_id = None

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
    return '{block_version}:{course_id}+type@{video_block_name}+block@{video_id}'.format(
        block_version=block_version,
        course_id=course_id,
        video_block_name=video_block_name,
        video_id=video_id
    )


def make_course_url(course_id):
    """
    Return course info url.

    Arguments:
        course_id       (str) : course key string

    Returns:
        str
    """
    if course_id is None:
        return None
    return '{root_url}{course_root_url}'.format(
        root_url=settings.LMS_ROOT_URL,
        course_root_url=reverse('course_root', kwargs={
            'course_id': course_id
        })
    )


def backend_cache_ttl():
    """
    Return cache time out.

    Returns:
        int
    """
    return getattr(settings, 'EVENT_TRACKING_BACKENDS_CACHE_TTL', 600)
