"""
Celery tasks.
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from celery_utils.persist_on_failure import LoggedPersistOnFailureTask
from django.conf import settings

from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

logger = get_task_logger(__name__)

ROUTER_STRATEGY_MAPPING = {
    'AUTH_HEADERS': HttpClient,
    'XAPI_LRS': LrsClient,
}


@shared_task(bind=True, base=LoggedPersistOnFailureTask)
def dispatch_event_persistent(self, event_name, event, router_type, host_config):
    """
    Send event to configured client.

    Arguments:
        self (object)       :  celery task object to perform celery actions
        event_name (str)    : name of the original event
        event (dict)        : event dictionary to be delivered.
        router_type (str)   : decides the client to use for sending the event
        host_config (dict)  : contains configurations for the host.
    """
    send_event(self, event_name, event, router_type, host_config)


@shared_task(bind=True,)
def dispatch_event(self, event_name, event, router_type, host_config):
    """
    Send event to configured client.

    Arguments:
        self (object)       : celery task object to perform celery actions
        event_name (str)    : name of the original event
        event (dict)        : event dictionary to be delivered.
        router_type (str)   : decides the client to use for sending the event
        host_config (dict)  : contains configurations for the host.
    """
    send_event(self, event_name, event, router_type, host_config)


def send_event(task, event_name, event, router_type, host_config):
    """
    Send event to configured client.

    Arguments:
        task (object)       : celery task object to perform celery actions
        event_name (str)    : name of the original event
        event (dict)        : event dictionary to be delivered.
        router_type (str)   : decides the client to use for sending the event
        host_config (dict)  : contains configurations for the host.
    """
    try:
        client_class = ROUTER_STRATEGY_MAPPING[router_type]
    except KeyError:
        logger.error('Unsupported routing strategy detected: {}'.format(router_type))
        return

    try:
        client = client_class(**host_config)
        client.send(event, event_name)
        logger.debug(
            'Successfully dispatched transformed version of edx event "{}" using client: {}'.format(
                event_name,
                client_class
            )
        )
    except EventNotDispatched as exc:
        logger.exception(
            'Exception occurred while trying to dispatch edx event "{}" using client: {}'.format(
                event_name,
                client_class
            ),
            exc_info=True
        )
        raise task.retry(exc=exc, countdown=getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 30),
                         max_retries=getattr(settings, ''
                                                       'EVENT_ROUTING_BACKEND_MAX_RETRIES', 3))


@shared_task(bind=True)
def dispatch_bulk_events(self, events, router_type, host_config):
    """
    Send a batch of events to the same configured client.

    Arguments:
        self (object)       : celery task object to perform celery actions
        events (list[dict]) : list of event dictionaries to be delivered.
        router_type (str)   : decides the client to use for sending the event
        host_config (dict)  : contains configurations for the host.
    """
    bulk_send_events(self, events, router_type, host_config)


def bulk_send_events(task, events, router_type, host_config):
    """
    Send event to configured client.

    Arguments:
        task (object)       : celery task object to perform celery actions
        events (list[dict]) : list of event dictionaries to be delivered.
        router_type (str)   : decides the client to use for sending the event
        host_config (dict)  : contains configurations for the host.
    """
    try:
        client_class = ROUTER_STRATEGY_MAPPING[router_type]
    except KeyError:
        logger.error('Unsupported routing strategy detected: {}'.format(router_type))
        return

    try:
        client = client_class(**host_config)
        client.bulk_send(events)
        logger.debug(
            'Successfully bulk dispatched transformed versions of {} events using client: {}'.format(
                len(events),
                client_class
            )
        )
    except EventNotDispatched as exc:
        logger.exception(
            'Exception occurred while trying to bulk dispatch {} events using client: {}'.format(
                len(events),
                client_class
            ),
            exc_info=True
        )
        raise task.retry(exc=exc, countdown=getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 30),
                         max_retries=getattr(settings, 'EVENT_ROUTING_BACKEND_MAX_RETRIES', 3))
