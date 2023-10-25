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

logger = logging.getLogger(__name__)


@receiver(TRACKING_EVENT_EMITTED)
def send_tracking_log_to_backends(sender, signal, **kwargs):
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

    django_tracker = get_tracker()

    backend = django_tracker.backends["xapi"]

    try:
        processed_event = backend.process_event(event)
        logger.info('Successfully processed event "{}"'.format(event["name"]))
    except EventEmissionExit:
        logger.info("[EventEmissionExit] skipping event {}".format(event["name"]))
        return
    send_event(backend.backend_name, processed_event)
