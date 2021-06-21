"""
Mixin for testing transformers for all of the currently supported events
"""
import json
import os
from abc import abstractmethod
from unittest.mock import patch

import ddt
from django.contrib.auth import get_user_model

from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin
from event_routing_backends.tests.factories import UserFactory

User = get_user_model()

TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

EVENT_FIXTURE_FILENAMES = [
    event_file_name for event_file_name in os.listdir(
        f'{TEST_DIR_PATH}/fixtures/current/'
    ) if event_file_name.endswith(".json")
]


class DummyTransformer(BaseTransformerMixin):
    required_fields = ('does_not_exist',)


@ddt.ddt
class TransformersTestMixin:
    """
    Test that supported events are transformed correctly.
    """
    # no limit to diff in the output of tests
    maxDiff = None

    registry = None
    EXCEPTED_EVENTS_FIXTURES_PATH = None

    def setUp(self):
        UserFactory.create(username='edx')

    def test_with_no_field_transformer(self):
        self.registry.register('test_event')(DummyTransformer)
        with self.assertRaises(ValueError):
            self.registry.get_transformer({
                'name': 'test_event'
            }).transform()

    def test_required_field_transformer(self):
        self.registry.register('test_event')(DummyTransformer)
        with self.assertRaises(ValueError):
            self.registry.get_transformer({
                 "name": "edx.course.enrollment.activated"
                 }).transform()

    @abstractmethod
    def compare_events(self, transformed_event, expected_event):
        """
        Every transformer's test case will implement its own logic to test
        events transformation
        """
    @patch('event_routing_backends.helpers.uuid4')
    @ddt.data(*EVENT_FIXTURE_FILENAMES)
    def test_event_transformer(self, event_filename, mocked_uuid4):
        mocked_uuid4.return_value = '32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb'
        input_event_file_path = '{test_dir}/fixtures/current/{event_filename}'.format(
            test_dir=TEST_DIR_PATH, event_filename=event_filename
        )

        # if an event's expected fixture doesn't exist, the test shouldn't fail.
        # evaluate transformation of only supported event fixtures.
        expected_event_file_path = '{expected_events_fixtures_path}/{event_filename}'.format(
            expected_events_fixtures_path=self.EXCEPTED_EVENTS_FIXTURES_PATH, event_filename=event_filename
        )

        if not os.path.isfile(expected_event_file_path):
            return

        with open(input_event_file_path) as current, open(expected_event_file_path) as expected:
            original_event = json.loads(current.read())
            expected_event = json.loads(expected.read())

            actual_transformed_event = self.registry.get_transformer(original_event).transform()

            self.compare_events(actual_transformed_event, expected_event)
