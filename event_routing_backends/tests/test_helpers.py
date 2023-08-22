"""
Test the helper methods.
"""
from unittest.mock import patch

from django.test import TestCase

from event_routing_backends.helpers import (
    get_anonymous_user_id,
    get_block_id_from_event_referrer,
    get_course_from_id,
    get_user_email,
    get_uuid5,
)
from event_routing_backends.tests.factories import UserFactory


class TestHelpers(TestCase):
    """
    Test the helper methods.
    """
    def setUp(self):
        super().setUp()
        UserFactory.create(username='edx', email='edx@example.com')

    def test_get_block_id_from_event_referrer_with_error(self):
        sample_event = {
            'context': {
                'referer': None
            }
        }
        self.assertEqual(get_block_id_from_event_referrer(sample_event['context']['referer']), None)

    def test_get_user_email(self):
        with patch('event_routing_backends.helpers.get_potentially_retired_user_by_username') as mock_pr_user:
            mock_pr_user.return_value = None
            email = get_user_email('unknown')
            self.assertEqual(email, 'unknown@example.com')
        with patch('event_routing_backends.helpers.get_potentially_retired_user_by_username') as mock_pr_user:
            mock_pr_user.side_effect = Exception('User not found')
            email = get_user_email('unknown')
            self.assertEqual(email, 'unknown@example.com')
        email = get_user_email('edx')
        self.assertEqual(email, 'edx@example.com')

    @patch('event_routing_backends.helpers.ExternalId')
    def test_get_anonymous_user_id_with_error(self, mocked_external_id):
        mocked_external_id.add_new_user_id.return_value = (None, False)
        # Test that a failure to add an external id raises an error
        with self.assertRaises(ValueError):
            get_anonymous_user_id('edx', 'XAPI')

        # Test that an unknown user raises this error
        with self.assertRaises(ValueError):
            get_anonymous_user_id('12345678', 'XAPI')

    def test_get_uuid5(self):
        actor = '''{
            "objectType": "Agent",
            "mbox": "mailto:edx@example.com"
        }'''
        verb = '''{
        "id": "http://id.tincanapi.com/verb/unregistered",
        "display": {
            "en": "unregistered"
        }'''
        timestamp = '2023-05-09T06:36:11.256Z'
        name = f'{actor}-{timestamp}'
        uuid_1 = get_uuid5(verb, name)
        uuid_2 = get_uuid5(verb, name)
        self.assertEqual(uuid_1, uuid_2)

        another_actor = '''{
            "objectType": "Agent",
            "mbox": "mailto:test@example.com"
        }'''
        name = f'{another_actor}-{timestamp}'
        uuid_3 = get_uuid5(verb, name)
        self.assertNotEqual(uuid_1, uuid_3)

    @patch('event_routing_backends.helpers.get_course_overviews')
    def test_get_course_from_id(self, mock_get_course_overviews):
        mock_get_course_overviews.return_value = []
        course = get_course_from_id("foo")
        self.assertEqual(course["display_name"], "Unknown Course")
