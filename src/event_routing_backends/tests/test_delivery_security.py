"""Native task/FailedTask and log-collector regression contracts."""

import json
import logging
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from celery import Task
from celery.exceptions import Retry
from celery_utils.models import FailedTask
from pythonjsonlogger.json import JsonFormatter

from event_routing_backends import tasks
from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched
from event_routing_backends.processors.xapi.event_transformers.problem_interaction_events import (
    BaseProblemCheckTransformer,
)
from event_routing_backends.security import CredentialSafeEventRoutingFilter
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

SECRET = 'test-only-event-routing-sentinel'
TASK_ID = '14d16d5b-2496-4074-9538-1022c50f6098'
INVOCATION = ('event.name', {'payload': SECRET}, 'AUTH_HEADERS', {
    'url': f'https://user:{SECRET}@example.invalid/events?key={SECRET}',
    'headers': {'Authorization': SECRET},
})


@pytest.mark.django_db
def test_native_failure_persistence_and_replay_refusal():
    """Actual Celery failure tracing invokes native persisted diagnostics."""
    client = Mock()
    client.send.side_effect = ValueError(SECRET)
    with patch.dict(tasks.ROUTER_STRATEGY_MAPPING, AUTH_HEADERS=Mock(return_value=client)):
        result = tasks.dispatch_event_persistent.apply(args=INVOCATION, task_id=TASK_ID, throw=False)
        assert result.failed()
        tasks.dispatch_event_persistent.apply(args=INVOCATION, task_id=TASK_ID, throw=False)
    assert FailedTask.objects.filter(task_id=TASK_ID).count() == 1
    row = FailedTask.objects.get(task_id=TASK_ID)
    assert row.task_name == tasks.dispatch_event_persistent.name
    assert row.args == []
    assert row.kwargs == {}
    assert SECRET not in json.dumps([row.args, row.kwargs, row.exc])
    with patch.object(Task, 'apply_async') as submit:
        with pytest.raises(ValueError, match='cannot be replayed'):
            row.reapply()
        submit.assert_not_called()


@pytest.mark.parametrize('task', [tasks.dispatch_event, tasks.dispatch_event_persistent, tasks.dispatch_bulk_events])
def test_submission_preserves_transport_but_hides_representations(task):
    """Sanitizing diagnostics must not corrupt events delivered to the broker."""
    args = INVOCATION if task != tasks.dispatch_bulk_events else ([{'payload': SECRET}], *INVOCATION[2:])
    with patch.object(Task, 'apply_async') as submit:
        task.apply_async(args=args, kwargs={}, argsrepr=SECRET, kwargsrepr=SECRET)
    assert submit.call_args.kwargs['args'] == args
    assert submit.call_args.kwargs['kwargs'] == {}
    assert SECRET not in submit.call_args.kwargs['argsrepr']
    assert SECRET not in submit.call_args.kwargs['kwargsrepr']


@pytest.mark.parametrize('bulk', [False, True])
@pytest.mark.parametrize('exception', [OSError, ConnectionRefusedError, EventNotDispatched])
def test_native_transport_retry_policy(bulk, exception, settings):
    """OS failures retry once through the original configurable native budget."""
    settings.EVENT_ROUTING_BACKEND_COUNTDOWN = 11
    settings.EVENT_ROUTING_BACKEND_MAX_RETRIES = 2
    client = Mock()
    client.send.side_effect = client.bulk_send.side_effect = exception(SECRET)
    task = Mock()
    task.retry.side_effect = Retry()
    method = tasks.bulk_send_events if bulk else tasks.send_event
    args = ([{'payload': SECRET}], *INVOCATION[2:]) if bulk else INVOCATION
    with patch.dict(tasks.ROUTER_STRATEGY_MAPPING, AUTH_HEADERS=Mock(return_value=client)):
        with pytest.raises(Retry):
            method(task, *args)
        retry = task.retry.call_args.kwargs
        assert retry['countdown'] == 11 and retry['max_retries'] == 2
        assert isinstance(retry['exc'], EventNotDispatched)
        assert SECRET not in str(retry['exc'])
        with pytest.raises(exception, match=SECRET):
            method(None, *args)


@pytest.mark.parametrize('source', ['server', 'browser'])
def test_problem_check_referer_is_browser_only(source):
    """Exercise the native decorated transformer, with actual event lookups."""
    transformer = BaseProblemCheckTransformer({
        'name': 'problem_check', 'context': {'event_source': source},
        'data': {'module_id': 'block-v1:org+course+run+type@problem+block@p'},
    })
    if source == 'server':
        with patch.object(transformer, 'get_object_iri',
                          side_effect=lambda kind, block: f'https://example.invalid/{block}'):
            assert transformer.get_object().id.endswith('+block@p')
    else:
        with pytest.raises(ValueError, match='context.referer'):
            transformer.get_object()


def test_problem_check_browser_uses_existing_referer_path():
    """The server correction preserves browser block extraction."""
    transformer = BaseProblemCheckTransformer({
        'name': 'problem_check', 'context': {'event_source': 'browser', 'course_id': 'course'},
        'referer': 'https://example.invalid/problem', 'data': {'module_id': 'browser-module'},
    })
    target = 'event_routing_backends.processors.xapi.event_transformers.problem_interaction_events.get_problem_block_id'
    with patch(target,
               return_value='browser-block') as extract:
        with patch.object(transformer, 'get_object_iri',
                          side_effect=lambda kind, block: f'https://example.invalid/{block}'):
            assert transformer.get_object().id.endswith('/browser-block')
    extract.assert_called_once_with('https://example.invalid/problem', transformer.event['data'], 'course')


@pytest.mark.django_db
def test_os_failure_exhausts_native_budget_and_persists_once(settings):
    """Actual eager Celery retries terminate rather than loop or fail early."""
    settings.EVENT_ROUTING_BACKEND_COUNTDOWN = 0
    settings.EVENT_ROUTING_BACKEND_MAX_RETRIES = 2
    client = Mock()
    client.send.side_effect = ConnectionRefusedError(SECRET)
    with patch.dict(tasks.ROUTER_STRATEGY_MAPPING, AUTH_HEADERS=Mock(return_value=client)):
        result = tasks.dispatch_event_persistent.apply(args=INVOCATION, task_id=TASK_ID, throw=False)
    assert result.failed()
    assert client.send.call_count == 3
    assert FailedTask.objects.filter(task_id=TASK_ID).count() == 1
    assert SECRET not in FailedTask.objects.get(task_id=TASK_ID).exc


@pytest.mark.parametrize('logger_name', [
    'event_routing_backends.tasks', 'event_routing_backends.utils.http_client',
    'event_routing_backends.utils.xapi_lrs_client', 'event_routing_backends.processors.custom',
])
def test_collected_json_records_have_no_payload_or_exception(logger_name):
    """Unknown structured extras, cached formatting and tracebacks are sinks too."""
    try:
        raise ValueError(SECRET)
    except ValueError:
        record = logging.LogRecord(logger_name, logging.ERROR, __file__, 1, 'response %s', (SECRET,), sys.exc_info())
    record.message = record.exc_text = record.stack_info = SECRET
    record.headers = {'Authorization': SECRET}
    record.data = {'payload': SECRET}
    record.task_id = TASK_ID
    assert CredentialSafeEventRoutingFilter().filter(record)
    formatted = JsonFormatter().format(record)
    assert SECRET not in formatted
    assert json.loads(formatted)['task_id'] == TASK_ID
    assert record.levelno == logging.ERROR


@pytest.mark.django_db
def test_real_failing_task_trace_is_scrubbed_before_collector(caplog):
    """Use Celery's real tracer, then the actual JSON collector formatter."""
    filter_ = CredentialSafeEventRoutingFilter()
    caplog.handler.addFilter(filter_)
    client = Mock()
    client.send.side_effect = ValueError(SECRET)
    try:
        with patch.dict(tasks.ROUTER_STRATEGY_MAPPING, AUTH_HEADERS=Mock(return_value=client)):
            with caplog.at_level(logging.DEBUG):
                result = tasks.dispatch_event_persistent.apply(args=INVOCATION, task_id=TASK_ID, throw=False)
        assert result.failed()
        traces = [record for record in caplog.records if record.name == 'celery.app.trace']
        assert traces and any(record.levelno >= logging.ERROR for record in traces)
        formatter = JsonFormatter()
        assert all(SECRET not in formatter.format(record) for record in caplog.records)
        assert traces[-1].data == {'name': tasks.dispatch_event_persistent.name, 'id': TASK_ID}
    finally:
        caplog.handler.removeFilter(filter_)


def test_unrelated_task_logs_are_unchanged():
    """Event containment must not suppress the diagnostics of other tasks."""
    record = logging.LogRecord('celery.app.trace', logging.ERROR, __file__, 1, '%(exc)s',
                               ({'name': 'some.other.task', 'exc': 'benign failure'},), None)
    before = dict(record.__dict__)
    assert CredentialSafeEventRoutingFilter().filter(record)
    assert record.__dict__ == before


@pytest.mark.parametrize('client_type', ['http', 'lrs'])
@pytest.mark.parametrize('bulk', [False, True])
def test_native_client_failure_logs_are_filtered(client_type, bulk, caplog):
    """Run the real HTTP/LRS diagnostic branches; substitute transport only."""
    filter_ = CredentialSafeEventRoutingFilter()
    caplog.handler.addFilter(filter_)
    url = f'https://user:{SECRET}@example.invalid/events?key={SECRET}'
    try:
        with caplog.at_level(logging.DEBUG):
            if client_type == 'http':
                client = HttpClient(url=url, headers={'Authorization': SECRET})
                response = SimpleNamespace(status_code=503, text=SECRET, request=SimpleNamespace(method='POST'))
                with patch('event_routing_backends.utils.http_client.requests.post', return_value=response) as post:
                    with pytest.raises(EventNotDispatched):
                        client.bulk_send([{'payload': SECRET}]) if bulk else client.send({'payload': SECRET}, SECRET)
                assert post.call_args.kwargs['headers']['Authorization'] == SECRET
                assert post.call_args.kwargs['url'] == url
            else:
                response = SimpleNamespace(success=False, response=SimpleNamespace(code=503, status=503),
                                           request=SimpleNamespace(method='POST', content=SECRET), data=SECRET)
                transport = Mock()
                transport.save_statement.return_value = transport.save_statements.return_value = response
                with patch('event_routing_backends.utils.xapi_lrs_client.RemoteLRS', return_value=transport):
                    client = LrsClient(url=url, auth_scheme='Bearer', auth_key=SECRET)
                with pytest.raises(EventNotDispatched):
                    client.bulk_send([{'payload': SECRET}]) if bulk else client.send({'payload': SECRET}, SECRET)
        records = [record for record in caplog.records if record.name.startswith('event_routing_backends.utils.')]
        assert records and any(record.levelno >= logging.WARNING for record in records)
        assert all(SECRET not in JsonFormatter().format(record) for record in records)
    finally:
        caplog.handler.removeFilter(filter_)


def test_filter_accepts_malformed_structured_task_names():
    """A malformed extra cannot crash credential containment."""
    record = logging.LogRecord('event_routing_backends.tasks', logging.ERROR, __file__, 1, SECRET,
                               ({'name': [SECRET], 'id': SECRET},), None)
    record.data = {'name': {SECRET: SECRET}}
    record.task_name = [SECRET]
    assert CredentialSafeEventRoutingFilter().filter(record)
    assert SECRET not in JsonFormatter().format(record)
