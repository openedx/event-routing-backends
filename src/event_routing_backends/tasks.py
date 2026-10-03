"""
Celery tasks.
"""
import logging

from celery import Task, shared_task
from celery.utils.log import get_task_logger
from celery_utils.persist_on_failure import PersistOnFailureTask
from django.conf import settings

from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

logger = get_task_logger(__name__)

ROUTER_STRATEGY_MAPPING = {
    'AUTH_HEADERS': HttpClient,
    'XAPI_LRS': LrsClient,
}


class CredentialSafeTask(Task):
    """Keep broker-visible argument representations credential free."""

    abstract = True

    def apply_async(self, args=None, kwargs=None, **options):
        """Deliver the original invocation with redacted diagnostic reprs."""
        options['argsrepr'] = '<event-routing arguments withheld>'
        options['kwargsrepr'] = '<event-routing arguments withheld>'
        return super().apply_async(args=args, kwargs=kwargs, **options)


class CredentialSafePersistOnFailureTask(CredentialSafeTask, PersistOnFailureTask):
    """Persist correlation only, rather than credentials or replayable events.

    FailedTask rows are diagnostic-only. Event recovery must use the original
    tracking log and current routing configuration. Native FailedTask.reapply
    fails before queueing, rather than sending a fabricated redacted event.
    """

    abstract = True

    def apply_async(self, args=None, kwargs=None, **options):
        """Refuse replay of the deliberately empty diagnostic invocation."""
        if not args and not kwargs:
            raise ValueError('Event-routing failure diagnostics cannot be replayed; recover from tracking logs')
        return super().apply_async(args=args, kwargs=kwargs, **options)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Use native failure persistence without the original arguments."""
        safe_exception = RuntimeError('Event-routing delivery failed; payload and exception withheld')
        return super().on_failure(safe_exception, task_id, (), {}, None)


@shared_task(bind=True, base=CredentialSafePersistOnFailureTask)
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


@shared_task(bind=True, base=CredentialSafeTask)
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
        task (object, optional) : celery task object to perform celery actions
        event_name (str)        : name of the original event
        event (dict)            : event dictionary to be delivered.
        router_type (str)       : decides the client to use for sending the event
        host_config (dict)      : contains configurations for the host.
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
    except (EventNotDispatched, OSError):
        logger.log(logging.WARNING if task else logging.ERROR, 'Event-routing dispatch failed')
        # If this function is called synchronously, we want to raise the exception
        # to inform about errors. If it's called asynchronously, we want to retry
        # the celery task till it succeeds or reaches max retries.
        if not task:
            raise
        raise task.retry(exc=EventNotDispatched('Event-routing delivery failed'),
                         countdown=getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 30),
                         max_retries=getattr(settings, ''
                                                       'EVENT_ROUTING_BACKEND_MAX_RETRIES', 3))


@shared_task(bind=True, base=CredentialSafeTask)
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
        task (object, optional) : celery task object to perform celery actions
        events (list[dict])     : list of event dictionaries to be delivered.
        router_type (str)       : decides the client to use for sending the event
        host_config (dict)      : contains configurations for the host.
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
    except (EventNotDispatched, OSError):
        logger.log(logging.WARNING if task else logging.ERROR, 'Event-routing bulk dispatch failed')
        # If this function is called synchronously, we want to raise the exception
        # to inform about errors. If it's called asynchronously, we want to retry
        # the celery task till it succeeds or reaches max retries.
        if not task:
            raise
        raise task.retry(exc=EventNotDispatched('Event-routing delivery failed'),
                         countdown=getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 30),
                         max_retries=getattr(settings, 'EVENT_ROUTING_BACKEND_MAX_RETRIES', 3))
