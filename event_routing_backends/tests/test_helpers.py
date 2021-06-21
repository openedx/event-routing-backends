"""
Test the helper methods.
"""
from unittest.mock import patch

from django.test import TestCase

from event_routing_backends.helpers import get_anonymous_user_id_by_username, get_block_id_from_event_referrer
from event_routing_backends.tests.factories import UserFactory


class TestHelpers(TestCase):
    """
    Test the helper methods.
    """
    def setUp(self):
        super().setUp()
        UserFactory.create(username='edx')

    def test_get_block_id_from_event_referrer_with_error(self):
        sample_event = {
            'context': {
                'referer': None
            }
        }
        self.assertEqual(get_block_id_from_event_referrer(sample_event['context']['referer']), None)

    @patch('event_routing_backends.helpers.ExternalId')
    def test_get_anonymous_user_id_by_username_with_error(self, mocked_external_id):
        mocked_external_id.add_new_user_id.return_value = (None, False)
        with self.assertRaises(ValueError):
            get_anonymous_user_id_by_username('edx')
