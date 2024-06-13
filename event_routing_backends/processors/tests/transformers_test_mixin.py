"""
Mixin for testing transformers for all of the currently supported events
"""
import json
import logging
import os
from abc import abstractmethod
from unittest.mock import patch
from uuid import UUID

import ddt
import pytest
from django.contrib.auth import get_user_model
from django.test.utils import override_settings

from event_routing_backends import __version__
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin
from event_routing_backends.tests.factories import UserFactory

logger = logging.getLogger(__name__)
User = get_user_model()

TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

try:
    EVENT_FIXTURE_FILENAMES = [
        event_file_name for event_file_name in os.listdir(
            f'{TEST_DIR_PATH}/fixtures/current/'
        ) if event_file_name.endswith(".json")
    ]

except FileNotFoundError as exc:  # pragma: no cover
    # This exception may happen when these test mixins are used outside of the ERB package.
    logger.exception(exc)
    EVENT_FIXTURE_FILENAMES = []


class DummyTransformer(BaseTransformerMixin):
    required_fields = ('does_not_exist',)


class TransformersFixturesTestMixin:
    """
    Mixin to help test event transforms using "raw" and "expected" fixture data.
    """
    # no limit to diff in the output of tests
    maxDiff = None

    registry = None

    def setUp(self):
        super().setUp()
        UserFactory.create(username='edx', email='edx@example.com')

    @property
    def raw_events_fixture_path(self):
        """
        Return the path to the raw events fixture files.
        """
        return f"{TEST_DIR_PATH}/fixtures/current"

    @property
    def expected_events_fixture_path(self):
        """
        Return the path to the expected transformed events fixture files.
        """
        raise NotImplementedError

    def get_raw_event(self, event_filename):
        """
        Return raw event json parsed from current fixtures
        """
        base_event_filename = os.path.basename(event_filename)

        input_event_file_path = '{test_dir}/{event_filename}'.format(
            test_dir=self.raw_events_fixture_path, event_filename=base_event_filename
        )
        with open(input_event_file_path, encoding='utf-8') as current:
            data = json.loads(current.read())
        return data

    @abstractmethod
    def compare_events(self, transformed_event, expected_event):
        """
        Every transformer's test case will implement its own logic to test
        events transformation
        """
        raise NotImplementedError

    def check_event_transformer(self, raw_event_file, expected_event_file):
        """
        Test that given event is transformed correctly.

        Transforms the contents of `raw_event_file` and compare it against the contents of `expected_event_file`.

        Writes errors to test_out/ for analysis.
        """
        original_event = self.get_raw_event(raw_event_file)
        with open(expected_event_file, encoding='utf-8') as expected:
            expected_event = json.loads(expected.read())

            event_filename = os.path.basename(raw_event_file)
            if "anonymous" in event_filename:
                with pytest.raises(ValueError):
                    self.registry.get_transformer(original_event).transform()
            else:
                actual_transformed_event = self.registry.get_transformer(original_event).transform()
                try:
                    self.compare_events(actual_transformed_event, expected_event)
                except Exception as e:  # pragma: no cover
                    print("Comparison failed, writing output to test_output for debugging")
                    with open(f"test_output/generated.{event_filename}.json", "w") as actual_transformed_event_file:
                        try:
                            actual_transformed_event_file.write(actual_transformed_event.to_json())
                        # Lists of events will trigger this exception and need to be transformed together
                        except AttributeError:
                            actual_transformed_event_file.write("[")
                            out_events = []
                            for event in actual_transformed_event:
                                out_events.append(event.to_json())
                            actual_transformed_event_file.write(",".join(out_events))
                            actual_transformed_event_file.write("]")

                    with open(f"test_output/expected.{raw_event_file}.json", "w") as test_output_file:
                        json.dump(expected_event, test_output_file, indent=4)

                    raise e


@ddt.ddt
class TransformersTestMixin:
    """
    Tests that supported events are transformed correctly.
    """
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

    @patch('event_routing_backends.helpers.uuid.uuid4')
    @ddt.data(*EVENT_FIXTURE_FILENAMES)
    def test_event_transformer(self, raw_event_file_path, mocked_uuid4):
        # Used to generate the anonymized actor.name,
        # which in turn is used to generate the event UUID.
        mocked_uuid4.return_value = UUID('32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb')

        # if an event's expected fixture doesn't exist, the test shouldn't fail.
        # evaluate transformation of only supported event fixtures.
        base_event_filename = os.path.basename(raw_event_file_path)

        expected_event_file_path = '{expected_events_fixture_path}/{event_filename}'.format(
            expected_events_fixture_path=self.expected_events_fixture_path, event_filename=base_event_filename
        )

        if not os.path.isfile(expected_event_file_path):
            return

        self.check_event_transformer(raw_event_file_path, expected_event_file_path)
