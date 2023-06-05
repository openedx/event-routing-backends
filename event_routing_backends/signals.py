import json
import logging

from django.conf import settings
from django.dispatch import receiver
from django_redis import get_redis_connection
from edx_django_utils.cache.utils import get_cache_key
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
    event = kwargs['tracking_log']

    ## TODO: Should we ignore events that we don't care about here or in the event routing backend config?

    redis = get_redis_connection("default")

    queue_size = redis.llen(TRANSFORMED_EVENT_KEY_NAME)
    if queue_size >= settings.EVENT_ROUTING_BATCH_SIZE:
        queued_events = redis.rpop(TRANSFORMED_EVENT_KEY_NAME, settings.EVENT_ROUTING_BATCH_SIZE)
        queued_events.append(event)
        ## TODO: Send events to event bus in batch
        logger.info("Sending events to event bus in batch")

        #if SEND_TRACKING_EVENT_EMITTED_SIGNAL.is_enabled():
        #    get_producer().send(
        #        signal=TRACKING_EVENT_EMITTED,
        #        topic='analytics',
        #        event_key_field='tracking_log.name',
        #        event_data={'tracking_log': kwargs['tracking_log']},
        #        event_metadata=kwargs['metadata']
        #    )
    else:
        redis.lpush(TRANSFORMED_EVENT_KEY_NAME, json.dumps({
            "name": event.name,
            "timestamp": event.timestamp,
            "data": event.data,
            "context": event.context,
        }))
        logger.info("Event pushed to the queue, current size: %s", queue_size + 1)
