import json
import logging

from django.conf import settings
from django.dispatch import receiver
from openedx_events.analytics.signals import TRACKING_EVENT_EMITTED
from openedx_events.event_bus import get_producer

from event_routing_backends.config import SEND_TRACKING_EVENT_EMITTED_SIGNAL

logger = logging.getLogger(__name__)

TRANSFORMED_EVENT_KEY_NAME = "transformed_events"

@receiver(TRACKING_EVENT_EMITTED)
def listen_for_tracking_event_emitted_event(sender, signal, **kwargs):
    """
    Publish `TRACKING_EVENT_EMITTED` events to the event bus.
    """

    if SEND_TRACKING_EVENT_EMITTED_SIGNAL.is_enabled():
        logger.info("Sending events to event bus in batch")
        get_producer().send(
            signal=TRACKING_EVENT_EMITTED,
            topic='analytics',
            event_key_field='tracking_log.name',
            event_data={'tracking_log': kwargs['tracking_log']},
            event_metadata=kwargs['metadata']
        )
