"""
Tests for the transform_tracking_logs management command.
"""

from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from eventtracking.django.django_tracker import DjangoTracker

from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched

XAPI_PROCESSOR = {
    "ENGINE": "event_routing_backends.backends.async_events_router.AsyncEventsRouter",
    "OPTIONS": {
        "processors": [
            {
                "ENGINE": "event_routing_backends.processors.xapi.transformer_processor.XApiProcessor",
                "OPTIONS": {},
            }
        ],
        "backend_name": "xapi",
    },
}

called = False


class Mocker:
    """Custom class that returns a list of failed events in the first call and an empty list in following calls"""

    def __init__(self):
        self.called = False

    def custom_get_failed_events(self, batch_size):
        if not self.called:
            self.called = True
            return [{"name": "test"}]
        return []


class TestRecoverFailedEvents(TestCase):
    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {
                    "backends": {"xapi": XAPI_PROCESSOR},
                },
            },
        }
    )
    @patch(
        "event_routing_backends.management.commands.recover_failed_events.get_tracker"
    )
    def test_send_tracking_log_to_backends(self, mock_get_tracker):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker
        mock_backend = Mock()
        tracker.backends["event_bus"].backends["xapi"] = mock_backend
        mock_backend.get_failed_events = Mocker().custom_get_failed_events

        call_command("recover_failed_events", transformer_type="all")

        mock_backend.send.assert_called_once_with({"name": "test"})

    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {
                    "backends": {"xapi": XAPI_PROCESSOR},
                },
            },
        }
    )
    @patch(
        "event_routing_backends.management.commands.recover_failed_events.get_tracker"
    )
    @patch("event_routing_backends.management.commands.recover_failed_events.logger")
    def test_send_tracking_log_to_backends_with_exception(
        self, mock_logger, mock_get_tracker
    ):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker
        mock_backend = Mock()
        tracker.backends["event_bus"].backends["xapi"] = mock_backend
        mock_backend.get_failed_events = Mocker().custom_get_failed_events
        mock_backend.send.side_effect = Exception("Error")

        call_command("recover_failed_events", transformer_type="all")

        mock_logger.error.assert_called_once_with("Failed to send event: Error")

    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {
                    "backends": {"xapi": XAPI_PROCESSOR},
                },
            },
        }
    )
    @patch(
        "event_routing_backends.management.commands.recover_failed_events.get_tracker"
    )
    @patch("event_routing_backends.management.commands.recover_failed_events.logger")
    def test_send_tracking_log_to_backends_with_event_exception(
        self, mock_logger, mock_get_tracker
    ):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker
        mock_backend = Mock()
        tracker.backends["event_bus"].backends["xapi"] = mock_backend
        mock_backend.get_failed_events = Mocker().custom_get_failed_events
        mock_backend.send.side_effect = EventNotDispatched("Error")

        call_command("recover_failed_events", transformer_type="all")

        mock_logger.error.assert_called_once_with("Malformed event: {}".format("test"))

    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {
                    "backends": {"xapi": XAPI_PROCESSOR},
                },
            },
            "xapi": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {
                    "backends": {"xapi": XAPI_PROCESSOR},
                },
            },
        }
    )
    @patch(
        "event_routing_backends.management.commands.recover_failed_events.get_tracker"
    )
    def test_send_tracking_log_to_backends_no_failed_events(self, mock_get_tracker):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker
        mock_backend = Mock()
        tracker.backends["xapi"].backends["xapi"] = mock_backend
        mock_backend.get_failed_events.return_value = []

        call_command("recover_failed_events", transformer_type="xapi")

        mock_backend.send.assert_not_called()

    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.logger.LoggerBackend",
                "OPTIONS": {},
            },
        }
    )
    @patch(
        "event_routing_backends.management.commands.recover_failed_events.get_tracker"
    )
    @patch("event_routing_backends.management.commands.recover_failed_events.logger")
    def test_send_tracking_log_to_backends_no_engines(
        self, mock_logger, mock_get_tracker
    ):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker

        call_command("recover_failed_events", transformer_type="all")

        mock_logger.info.assert_any_call("Recovering failed events")
        mock_logger.info.assert_any_call("No compatible backend found.")
