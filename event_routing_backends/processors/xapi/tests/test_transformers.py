"""
Test the transformers for all of the currently supported events into xAPI format.
"""
import json
import os

from django.test import TestCase

from event_routing_backends.processors.tests.transformers_test_mixin import TransformersTestMixin
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry


class TestXApiTransformers(TransformersTestMixin, TestCase):
    """
    Test that supported events are transformed into xAPI format correctly.
    """
    EXCEPTED_EVENTS_FIXTURES_PATH = '{}/fixtures/expected'.format(os.path.dirname(os.path.abspath(__file__)))
    registry = XApiTransformersRegistry

    def compare_events(self, transformed_event, expected_event):
        """
        Test that transformed_event and expected_event are identical.

        Arguments:
            transformed_event (dict)
            expected_event (dict)

        Raises:
            AssertionError:     Raised if the two events are not same.
        """
        # id is a randomly generated UUID therefore not comparing that
        transformed_event_json = json.loads(transformed_event.to_json())
        self.assertIn('id', transformed_event_json)
        expected_event.pop('id')
        transformed_event_json.pop('id')
        self.assertDictEqual(expected_event, transformed_event_json)
