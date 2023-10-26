"""
This module contains the handlers for signals emitted by the analytics app.
"""
import json
import logging

from django.dispatch import receiver
from eventtracking.processors.exceptions import EventEmissionExit
from eventtracking.tasks import send_event
from eventtracking.tracker import get_tracker
from openedx_events.analytics.signals import TRACKING_EVENT_EMITTED

from eventtracking.backends.event_bus import EVENT_BUS_SOURCE

from eventtracking.backends.event_bus import EventBusRoutingBackend

logger = logging.getLogger(__name__)


@receiver(TRACKING_EVENT_EMITTED)
def send_tracking_log_to_backends(sender, signal, **kwargs):
    """
    Listen for the TRACKING_EVENT_EMITTED signal and send the event to the enabled backend.
    """
    metadata = kwargs.get("metadata")
    if EVENT_BUS_SOURCE != metadata.source:
        # This event cannot be processed by the same service that produced it.
        # We need to wait for the event to be processed by the event bus.
        logger.info("Event in same source, skipping event")
        return

    tracking_log = kwargs.get("tracking_log")

    event = {
        "name": tracking_log.name,
        "timestamp": tracking_log.timestamp,
        "data": json.loads(tracking_log.data),
        "context": json.loads(tracking_log.context),
    }

    tracker = get_tracker()

    engines = {name: engine for name,engine in tracker.backends.items() if isinstance(engine, EventBusRoutingBackend)}
    for name, engine in engines.items():
        try:
            processed_event = engine.process_event(event)
            logger.info('Successfully processed event "{}"'.format(event["name"]))
        except EventEmissionExit:
            logger.info("[EventEmissionExit] skipping event {}".format(event["name"]))
            return
        send_event(name, processed_event)
