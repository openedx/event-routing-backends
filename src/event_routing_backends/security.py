"""Credential-free diagnostics for event delivery.

Install ``CredentialSafeEventRoutingFilter`` using Django's LOGGING setting on
the Celery trace logger and every collected handler. Handler coverage also
protects diagnostics from children of the event-routing logger. This module
does not import Django models, so dictConfig can load it before apps are ready.
"""

import logging
import uuid

EVENT_ROUTING_TASKS = frozenset({
    'event_routing_backends.tasks.dispatch_event',
    'event_routing_backends.tasks.dispatch_event_persistent',
    'event_routing_backends.tasks.dispatch_bulk_events',
})
_STANDARD_RECORD_FIELDS = frozenset(logging.LogRecord('', 0, '', 0, '', (), None).__dict__)


class CredentialSafeEventRoutingFilter(logging.Filter):
    """Remove payloads, arbitrary extras and exception text before formatting.

    Delivery credentials can appear anywhere in a URL, event, response or
    exception; key-name or token-pattern redaction is insufficient. Retain
    severity, source location and validated Celery task correlation only.
    Other applications' records pass through unchanged.
    """

    def filter(self, record):
        """Scrub routing diagnostics and routing-task Celery trace records."""
        contexts = [value for value in (record.args, getattr(record, 'data', None))
                    if isinstance(value, dict)]
        task_name = next((value.get('name') for value in contexts
                          if isinstance(value.get('name'), str) and value['name'] in EVENT_ROUTING_TASKS), None)
        explicit_task_name = getattr(record, 'task_name', None)
        if task_name is None and isinstance(explicit_task_name, str) and explicit_task_name in EVENT_ROUTING_TASKS:
            task_name = explicit_task_name
        routing_logger = record.name == 'event_routing_backends' or record.name.startswith('event_routing_backends.')
        if not routing_logger and not (record.name == 'celery.app.trace' and task_name):
            return True
        task_id = next((value.get('id') for value in contexts if value.get('name') == task_name), None)
        if task_id is None:
            task_id = getattr(record, 'task_id', None)
        try:
            task_id = str(uuid.UUID(task_id)) if isinstance(task_id, str) else 'unknown'
        except ValueError:
            task_id = 'unknown'
        for key in tuple(record.__dict__):
            if key not in _STANDARD_RECORD_FIELDS:
                del record.__dict__[key]
        record.msg = 'Event-routing diagnostic (payload and exception withheld)'
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        record.task_name = task_name or 'event-routing'
        record.task_id = task_id
        record.data = {'name': record.task_name, 'id': task_id}
        return True
