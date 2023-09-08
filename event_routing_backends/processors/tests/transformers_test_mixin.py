"""
Mixin for testing transformers for all of the currently supported events
"""
import json
import os
from abc import abstractmethod
from unittest.mock import patch

import ddt
import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from event_routing_backends import __version__
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
        UserFactory.create(username='edx', email='edx@example.com')

    def get_raw_event(self, event_filename):
        """
        Return raw event json parsed from current fixtures
        """

        input_event_file_path = '{test_dir}/fixtures/current/{event_filename}'.format(
            test_dir=TEST_DIR_PATH, event_filename=event_filename
        )
        with open(input_event_file_path, encoding='utf-8') as current:
            data = json.loads(current.read())
        return data

    @override_settings(RUNNING_WITH_TEST_SETTINGS=True)
    def test_transformer_version_with_test_settings(self):
        self.registry.register('test_event')(DummyTransformer)
        raw_event = self.get_raw_event('edx.course.enrollment.activated.json')
        transformed_event = self.registry.get_transformer(raw_event).transform()
        self.assert_correct_transformer_version(transformed_event, 'event-routing-backends@1.1.1')

    @override_settings(RUNNING_WITH_TEST_SETTINGS=False)
    def test_transformer_version(self):
        self.registry.register('test_event')(DummyTransformer)
        raw_event = self.get_raw_event('edx.course.enrollment.activated.json')
        transformed_event = self.registry.get_transformer(raw_event).transform()
        self.assert_correct_transformer_version(transformed_event, 'event-routing-backends@{}'.format(__version__))

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
    @patch('event_routing_backends.helpers.uuid')
    @ddt.data(*EVENT_FIXTURE_FILENAMES)
    def test_event_transformer(self, event_filename, mocked_uuid):
        mocked_uuid.uuid4.return_value = '32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb'
        mocked_uuid.uuid5.return_value = '32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb'

        # if an event's expected fixture doesn't exist, the test shouldn't fail.
        # evaluate transformation of only supported event fixtures.
        expected_event_file_path = '{expected_events_fixtures_path}/{event_filename}'.format(
            expected_events_fixtures_path=self.EXCEPTED_EVENTS_FIXTURES_PATH, event_filename=event_filename
        )

        if not os.path.isfile(expected_event_file_path):
            return

        original_event = self.get_raw_event(event_filename)
        with open(expected_event_file_path, encoding='utf-8') as expected:
            expected_event = json.loads(expected.read())

            if "anonymous" in event_filename:
                with pytest.raises(ValueError):
                    self.registry.get_transformer(original_event).transform()
            else:
                actual_transformed_event = self.registry.get_transformer(original_event).transform()
                try:
                    self.compare_events(actual_transformed_event, expected_event)
                except Exception as e:  # pragma: no cover
                    with open(f"test_output/generated.{event_filename}.json", "w") as actual_transformed_event_file:
                        actual_transformed_event_file.write(actual_transformed_event.to_json())

                    with open(f"test_output/expected.{event_filename}.json", "w") as expected_event_file:
                        json.dump(expected_event, expected_event_file, indent=4)

                    raise e
