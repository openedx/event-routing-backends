"""
Test the xAPI processor.
"""

from django.test import SimpleTestCase
from django.test.utils import override_settings
from eventtracking.processors.exceptions import EventEmissionExit
from mock import MagicMock, call, patch, sentinel
from tincan import Statement

from event_routing_backends.processors.xapi.transformer_processor import XApiProcessor


@override_settings(XAPI_EVENTS_ENABLED=True)
class TestXApiProcessor(SimpleTestCase):
    """Test cases for xAPI processor"""

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.processor = XApiProcessor()

    @override_settings(XAPI_EVENTS_ENABLED=False)
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
        'event_routing_backends.processors.xapi.transformer_processor.XApiTransformersRegistry.get_transformer',
        side_effect=ValueError('Generic Error')
    )
    @patch('event_routing_backends.processors.mixins.base_transformer_processor.logger')
    def test_send_method_with_unknown_exception(self, mocked_logger, _):
        with self.assertRaises(ValueError):
            self.processor(self.sample_event)

        mocked_logger.exception.assert_called_once_with(
            'There was an error while trying to transform event "sentinel.name" using XApiProcessor'
            ' processor. Error: Generic Error')

    @patch(
        'event_routing_backends.processors.xapi.transformer_processor.XApiTransformersRegistry.get_transformer'
    )
    @patch('event_routing_backends.processors.xapi.transformer_processor.xapi_logger')
    def test_send_method_with_successfull_flow(self, mocked_logger, mocked_get_transformer):
        transformed_event = Statement()
        mocked_transformer = MagicMock()
        mocked_transformer.transform.return_value = transformed_event
        mocked_get_transformer.return_value = mocked_transformer

        self.processor(self.sample_event)

        self.assertIn(call(transformed_event.to_json()), mocked_logger.mock_calls)

    @patch('event_routing_backends.processors.mixins.base_transformer_processor.logger')
    def test_with_no_registry(self, mocked_logger):
        backend = XApiProcessor()
        backend.registry = None
        with self.assertRaises(EventEmissionExit):
            self.assertIsNone(backend(self.sample_event))
        mocked_logger.exception.assert_called_once()
