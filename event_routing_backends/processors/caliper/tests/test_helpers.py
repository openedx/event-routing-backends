"""
Test the helper methods.
"""
from django.test import TestCase

from event_routing_backends.processors.caliper.helpers import get_block_id_from_event_referrer


class TestHelpers(TestCase):
    """
    Test the helper methods.
    """
    def test_get_block_id_from_event_referrer_with_error(self):
        sample_event = {
            'context': {}
        }
        self.assertIsNone(get_block_id_from_event_referrer(sample_event))
