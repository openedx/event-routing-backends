import logging

from django.dispatch import receiver
from openedx_events.analytics.signals import TRACKING_EVENT_EMITTED_TO_BUS

logger = logging.getLogger(__name__)

@receiver(TRACKING_EVENT_EMITTED_TO_BUS)
def listen_for_tracking_event_emitted_event(sender, signal, **kwargs):
    """
    Publish `TRACKING_EVENT_EMITTED` events to the event bus.
    """
    print("\nSay hi from event bus\n")
