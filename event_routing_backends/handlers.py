"""
This module contains the handlers for signals emitted by the analytics app.
"""
import json
import logging

from django.dispatch import receiver
from eventtracking.backends.event_bus import EventBusRoutingBackend
from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.tasks import send_event
from eventtracking.tracker import get_tracker
from openedx_events.analytics.signals import TRACKING_EVENT_EMITTED

logger = logging.getLogger(__name__)


@receiver(TRACKING_EVENT_EMITTED)
def send_tracking_log_to_backends(
    sender, signal, **kwargs
):  # pylint: disable=unused-argument
    """
    Listen for the TRACKING_EVENT_EMITTED signal and send the event to the enabled backend.
    """
    tracking_log = kwargs.get("tracking_log")

    event = {
        "name": tracking_log.name,
        "timestamp": tracking_log.timestamp,
        "data": json.loads(tracking_log.data),
        "context": json.loads(tracking_log.context),
    }

    tracker = get_tracker()

    engines = {
        name: engine
        for name, engine in tracker.backends.items()
        if isinstance(engine, EventBusRoutingBackend)
    }
    for name, engine in engines.items():
        try:
            processed_event = engine.process_event(event)
            logger.info('Successfully processed event "{}"'.format(event["name"]))
            send_event(name, processed_event, True)
        except EventEmissionExit:
            logger.info("[EventEmissionExit] skipping event {}".format(event["name"]))
            return
