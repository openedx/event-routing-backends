"""
Test handlers for signals emitted by the analytics app
"""

from unittest.mock import Mock, patch

from django.test import TestCase
from django.test.utils import override_settings
from eventtracking.django.django_tracker import DjangoTracker
from eventtracking.processors.exceptions import EventEmissionExit
from openedx_events.analytics.data import TrackingLogData

from event_routing_backends.handlers import send_tracking_log_to_backends


class TestHandlers(TestCase):
    """
    Tests handlers for signals emitted by the analytics app
    """

    @override_settings(
        EVENT_TRACKING_BACKENDS={
            "event_bus": {
                "ENGINE": "eventtracking.backends.event_bus.EventBusRoutingBackend",
                "OPTIONS": {},
            },
        }
    )
    @patch("event_routing_backends.handlers.get_tracker")
    @patch("event_routing_backends.handlers.isinstance")
    @patch("event_routing_backends.handlers.send_event")
    def test_send_tracking_log_to_backends(
        self, mock_send_event, mock_is_instance, mock_get_tracker
    ):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker

        mock_is_instance.return_value = True

        mock_send_event.return_value = None

        send_tracking_log_to_backends(
            sender=None,
            signal=None,
            tracking_log=TrackingLogData(
                name="test_name",
                timestamp="test_timestamp",
                data="{}",
                context="{}",
            ),
        )

        mock_send_event.assert_called_once_with(
            "event_bus",
            {
                "name": "test_name",
                "timestamp": "test_timestamp",
                "data": {},
                "context": {},
            },
            True,
        )

    @patch("event_routing_backends.handlers.get_tracker")
    @patch("event_routing_backends.handlers.isinstance")
    @patch(
        "event_routing_backends.handlers.send_event",
        **{"return_value.raiseError.side_effect": EventEmissionExit()}
    )
    @patch("event_routing_backends.handlers.logger")
    def test_send_tracking_log_to_backends_error(
        self, mock_logger, mock_send_event, mock_is_instance, mock_get_tracker
    ):
        """
        Test for send_tracking_log_to_backends
        """
        tracker = DjangoTracker()
        mock_get_tracker.return_value = tracker

        mock_is_instance.return_value = True

        x = send_tracking_log_to_backends(
            sender=None,
            signal=None,
            tracking_log=TrackingLogData(
                name="test_name",
                timestamp="test_timestamp",
                data="{}",
                context="{}",
            ),
        )

        assert x is None

        # mock_logger.info.assert_called_once_with(
        #     "[EventEmissionExit] skipping event {}".format("test_name")
        # )
