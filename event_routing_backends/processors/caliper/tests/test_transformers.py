"""
Test the transformers for all of the currently supported events into Caliper format.
"""
import os
from unittest.mock import patch

from django.test import TestCase

from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.tests.transformers_test_mixin import TransformersTestMixin
from test_utils import mocked_course_reverse


class TestCaliperTransformers(TransformersTestMixin, TestCase):
    """
    Test that supported events are transformed into Caliper format correctly.
    """
    EXCEPTED_EVENTS_FIXTURES_PATH = '{}/fixtures/expected'.format(os.path.dirname(os.path.abspath(__file__)))

    registry = CaliperTransformersRegistry

    def setUp(self):
        super().setUp()
        self.mocked_reverse = patch(
            'event_routing_backends.helpers.reverse',
            side_effect=mocked_course_reverse
        )
        self.mocked_reverse.start()
        self.addCleanup(self.mocked_reverse.stop)

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
        self.assertIn('id', transformed_event)
        expected_event.pop('id')
        transformed_event.pop('id')
        self.assertDictEqual(expected_event, transformed_event)
