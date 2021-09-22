"""
Celery tasks.
"""
from celery import shared_task
from celery.utils.log import get_task_logger
from celery_utils.persist_on_failure import LoggedPersistOnFailureTask

from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

logger = get_task_logger(__name__)

ROUTER_STRATEGY_MAPPING = {
    'AUTH_HEADERS': HttpClient,
    'XAPI_LRS': LrsClient,
}

# Maximum number of retries before giving up
MAX_RETRIES = 3
# Number of seconds after task is retried
COUNTDOWN = 30


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
    logger.debug(
        'Routing event "%s" for router type "%s"',
        event_name,
        router_type
    )

    try:
        client_class = ROUTER_STRATEGY_MAPPING[router_type]
    except KeyError:
        logger.error('Unsupported routing strategy detected: {}'.format(router_type))
        return

    try:
        client = client_class(**host_config)
        client.send(event)
        logger.debug(
            'Successfully dispatched event "{}" using client strategy "{}"'.format(
                event_name,
                router_type
            )
        )
    except EventNotDispatched as exc:
        logger.exception(
            'Exception occurred while trying to dispatch event "{}"'.format(
                event_name,
            ),
            exc_info=True
        )
        raise task.retry(exc=exc, countdown=COUNTDOWN, max_retries=MAX_RETRIES)
