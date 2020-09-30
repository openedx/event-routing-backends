"""
Test utilities.

Since pytest discourages putting __init__.py into testdirectory
(i.e. making tests a package) one cannot import from anywhere
under tests folder. However, some utility classes/methods might be useful
in multiple test modules (i.e. factoryboy factories, base test classes).

So this package is the place to put them.
"""
import sys

import mock


def _mock_third_party_modules():
    """
    Mock third party modules used in the app.
    """
    # mock external_user_ids module
    external_id = mock.MagicMock()
    external_id.external_user_id = '32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb'
    external_user_ids_module = mock.MagicMock()
    external_user_ids_module.ExternalId.add_new_user_id.return_value = (external_id, True)
    external_user_ids_module.ExternalIdType.LTI = 'lti'
    sys.modules['openedx.core.djangoapps.external_user_ids.models'] = external_user_ids_module

    # mock course
    mocked_course = {
        'display_name': 'Demonstration Course',
    }

    mocked_courses = mock.MagicMock()
    mocked_courses.get_course_overviews.return_value = [mocked_course]
    sys.modules['openedx.core.djangoapps.content.course_overviews.api'] = mocked_courses

    # mock opaque keys module
    mocked_keys = mock.MagicMock()
    sys.modules['opaque_keys.edx.keys'] = mocked_keys


def mocked_course_reverse(_, kwargs):
    """
    Return the reverse method to return course root URL.
    """
    return '/courses/{}/'.format(kwargs.get('course_id'))
