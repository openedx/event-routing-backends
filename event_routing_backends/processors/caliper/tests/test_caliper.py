"""
Test the caliper processor.
"""
import json

from django.test import SimpleTestCase
from django.test.utils import override_settings
from eventtracking.processors.exceptions import EventEmissionExit
from mock import MagicMock, call, patch, sentinel

from event_routing_backends.processors.caliper.transformer_processor import CaliperProcessor


@override_settings(CALIPER_EVENTS_ENABLED=True)
class TestCaliperProcessor(SimpleTestCase):
    """Test cases for Caliper processor"""

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.routers = {
            '0': MagicMock(),
            '1': MagicMock(),
        }

        self.processor = CaliperProcessor()

    @override_settings(CALIPER_EVENTS_ENABLED=False)
    def test_skip_event_when_disabled(self):
        with self.assertRaises(EventEmissionExit):
            self.processor(self.sample_event)

    @patch('event_routing_backends.processors.mixins.base_transformer_processor.logger')
    def test_send_method_with_no_transformer_implemented(self, mocked_logger):
        with self.assertRaises(EventEmissionExit):
            self.processor(self.sample_event)

        mocked_logger.error.assert_called_once_with(
            'Could not get transformer for %s event.',
            self.sample_event.get('name')
        )

    @patch(
        'event_routing_backends.processors.caliper.transformer_processor.CaliperTransformersRegistry.get_transformer',
        side_effect=ValueError('Error Message')
    )
    @patch('event_routing_backends.processors.mixins.base_transformer_processor.logger')
    def test_send_method_with_unknown_exception(self, mocked_logger, _):
        with self.assertRaises(ValueError):
            self.processor(self.sample_event)

        mocked_logger.exception.assert_called_once_with(
            'There was an error while trying to transform event "sentinel.name" using CaliperProcessor'
            ' processor. Error: Error Message')

    @patch(
        'event_routing_backends.processors.caliper.transformer_processor.CaliperTransformersRegistry.get_transformer'
    )
    @patch('event_routing_backends.processors.caliper.transformer_processor.caliper_logger')
    def test_send_method_with_successfull_flow(self, mocked_logger, mocked_get_transformer):
        transformed_event = {
            'transformed_key': 'transformed_value'
        }
        mocked_transformer = MagicMock()
        mocked_transformer.transform.return_value = transformed_event
        mocked_get_transformer.return_value = mocked_transformer

        self.processor(self.sample_event)

        self.assertIn(call(json.dumps(transformed_event)), mocked_logger.mock_calls)

    @patch('event_routing_backends.processors.mixins.base_transformer_processor.logger')
    def test_with_no_registry(self, mocked_logger):
        backend = CaliperProcessor()
        backend.registry = None
        with self.assertRaises(EventEmissionExit):
            self.assertIsNone(backend(self.sample_event))
        mocked_logger.exception.assert_called_once()
