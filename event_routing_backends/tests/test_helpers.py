"""
Test the helper methods.
"""
from unittest.mock import patch

from django.test import TestCase

from event_routing_backends.helpers import get_anonymous_user_id, get_block_id_from_event_referrer, get_user_email
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
        with self.assertRaises(ValueError):
            get_anonymous_user_id('edx', 'XAPI')

        self.assertIsNotNone(get_anonymous_user_id('12345678', 'XAPI'))
