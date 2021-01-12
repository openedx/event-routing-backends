"""
Test the transformers for all of the currently supported events into xAPI format.
"""
import json
import os
from unittest.mock import patch

from django.test import TestCase

from event_routing_backends.processors.tests.transformers_test_mixin import TransformersTestMixin
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from test_utils import mocked_course_reverse


class TestXApiTransformers(TransformersTestMixin, TestCase):
    """
    Test that supported events are transformed into xAPI format correctly.
    """
    EXCEPTED_EVENTS_FIXTURES_PATH = '{}/fixtures/expected'.format(os.path.dirname(os.path.abspath(__file__)))
    registry = XApiTransformersRegistry

    def setUp(self):
        super().setUp()
        self.mocked_reverse_calls = [
            patch(call_path, side_effect=mocked_course_reverse) for call_path in [
                'event_routing_backends.helpers.reverse',
            ]
        ]
        for mocked in self.mocked_reverse_calls:
            mocked.start()
            self.addCleanup(mocked.stop)

    def compare_events(self, transformed_event, expected_event):
        """
        Test that transformed_event and expected_event are identical.

        Arguments:
            transformed_event (dict)
            expected_event (dict)

        Raises:
            AssertionError:     Raised if the two events are not same.
        """
        self.assertDictEqual(expected_event, json.loads(transformed_event.to_json()))
