"""
Test the transformers for all of the currently supported events into xAPI format.
"""
import hashlib
import json
import os

from django.test import TestCase
from django.test.utils import override_settings

from event_routing_backends.processors.tests.transformers_test_mixin import TransformersTestMixin
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class TestXApiTransformers(TransformersTestMixin, TestCase):
    """
    Test that supported events are transformed into xAPI format correctly.
    """
    EXCEPTED_EVENTS_FIXTURES_PATH = '{}/fixtures/expected'.format(os.path.dirname(os.path.abspath(__file__)))
    registry = XApiTransformersRegistry

    def assert_correct_transformer_version(self, transformed_event, transformer_version):
        self.assertEqual(
            transformed_event.context.extensions[constants.XAPI_TRANSFORMER_VERSION_KEY],
            transformer_version
        )

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

    @override_settings(XAPI_AGENT_IFI_TYPE='mbox')
    def test_xapi_agent_ifi_settings_mbox(self):
        self.registry.register('test_event')(XApiTransformer)
        raw_event = self.get_raw_event('edx.course.enrollment.activated.json')
        transformed_event = self.registry.get_transformer(raw_event).transform()
        action_json = transformed_event.actor.to_json()
        self.assertEqual(action_json, json.dumps({"objectType": "Agent", "mbox": "mailto:edx@example.com"}))

    @override_settings(XAPI_AGENT_IFI_TYPE='mbox_sha1sum')
    def test_xapi_agent_ifi_settings_mbox_sha1sum(self):
        self.registry.register('test_event')(XApiTransformer)
        raw_event = self.get_raw_event('edx.course.enrollment.activated.json')
        transformed_event = self.registry.get_transformer(raw_event).transform()
        action_json = transformed_event.actor.to_json()
        mbox_sha1sum = hashlib.sha1('edx@example.com'.encode('utf-8')).hexdigest()
        self.assertEqual(
            action_json, json.dumps({"objectType": "Agent", "mbox_sha1sum": mbox_sha1sum})
        )
