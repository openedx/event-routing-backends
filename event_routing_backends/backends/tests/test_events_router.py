"""
Test the EventsRouter
"""
from unittest.mock import MagicMock, call, patch, sentinel

import ddt
from django.conf import settings
from django.test import TestCase
from edx_django_utils.cache.utils import TieredCache
from eventtracking.processors.exceptions import EventEmissionExit
from tincan.statement import Statement

from event_routing_backends.backends.events_router import EventsRouter
from event_routing_backends.helpers import get_business_critical_events
from event_routing_backends.models import RouterConfiguration
from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched
from event_routing_backends.tests.factories import RouterConfigurationFactory
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

ROUTER_CONFIG_FIXTURE = [
    {
        'headers': {},
        'match_params': {
            'data.key': 'value'
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'match_params': {
            'data.key': 'value1'
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'match_params': {
            'data.key': 'value'
        }
    },
    {
        'match_params': {},
        'host_configurations': {
            'version': '1.0.1',
        }
    }
]


@ddt.ddt
class TestEventsRouter(TestCase):
    """
    Test the EventsRouter
    """

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name),
            'event_type': 'edx.test.event',
            'time': '2020-01-01T12:12:12.000000+00:00',
            'data': {
                'key': 'value'
            },
            'context': {
                'username': 'testuser'
            },
            'session': '0000'
        }

        self.transformed_event = {
            'name': str(sentinel.name),
            'transformed': True,
            'event_time': '2020-01-01T12:12:12.000000+00:00',
            'data': {
                'key': 'value'
            },
        }

        self.router = EventsRouter(processors=[], backend_name='test')

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_processor_exception(self, mocked_logger, mocked_post):
        processors = [
            MagicMock(return_value=self.transformed_event),
            MagicMock(side_effect=EventEmissionExit, return_value=self.transformed_event),
            MagicMock(return_value=self.transformed_event),
        ]
        processors[1].side_effect = EventEmissionExit

        router = EventsRouter(processors=processors, backend_name='test')
        router.send(self.transformed_event)

        processors[0].assert_called_once_with(self.transformed_event)
        processors[1].assert_called_once_with(self.transformed_event)
        processors[2].assert_not_called()

        mocked_post.assert_not_called()

        self.assertIn(call(
            'Could not process edx event "%s" for backend %s\'s router',
            self.transformed_event['name'],
            'test',
            exc_info=True
        ), mocked_logger.error.mock_calls)

    @patch.dict('event_routing_backends.tasks.ROUTER_STRATEGY_MAPPING', {
        'AUTH_HEADERS': MagicMock(side_effect=EventNotDispatched)
    })
    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.tasks.logger')
    def test_generic_exception_business_critical_event(self, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name=RouterConfiguration.XAPI_BACKEND,
            enabled=True,
            route_url='http://test3.com',
            auth_scheme=RouterConfiguration.AUTH_BEARER,
            auth_key='test_key',
            configurations=ROUTER_CONFIG_FIXTURE[0]
        )

        router = EventsRouter(processors=[], backend_name=RouterConfiguration.CALIPER_BACKEND)
        event_data = self.transformed_event.copy()
        business_critical_events = get_business_critical_events()
        event_data['name'] = business_critical_events[0]
        router.send(event_data)

        self.assertEqual(mocked_logger.exception.call_count,
                         getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 3) + 1)
        mocked_post.assert_not_called()

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_no_router_configurations_available(self, mocked_logger, mocked_post):
        router = EventsRouter(processors=[], backend_name='test')
        router.send(self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call('Could not find any enabled router configuration for backend %s', 'test'),
            mocked_logger.error.mock_calls
        )

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.tasks.logger')
    def test_with_unsupported_routing_strategy(self, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name='test_backend',
            enabled=True,
            route_url='http://test3.com',
            auth_scheme=RouterConfiguration.AUTH_BEARER,
            auth_key='test_key',
            configurations=ROUTER_CONFIG_FIXTURE[0]
        )

        router = EventsRouter(processors=[], backend_name='test_backend')
        TieredCache.dangerous_clear_all_tiers()
        router.send(self.transformed_event)

        mocked_logger.error.assert_called_once_with('Unsupported routing strategy detected: INVALID_TYPE')
        mocked_post.assert_not_called()

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_no_available_hosts(self, mocked_logger, mocked_post):
        router_config = RouterConfigurationFactory.create(
            backend_name='test_backend',
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[1]
        )

        router = EventsRouter(processors=[], backend_name='test_backend')
        TieredCache.dangerous_clear_all_tiers()
        router.send(self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call(
                'Event %s is not allowed to be sent to any host for router %s with backend "%s"',
                self.transformed_event['name'], router_config.route_url, 'test_backend'
            ),
            mocked_logger.info.mock_calls
        )

    @ddt.data(
        (
            RouterConfiguration.XAPI_BACKEND,
        ),
        (
            RouterConfiguration.CALIPER_BACKEND,
        )
    )
    @patch.dict('event_routing_backends.tasks.ROUTER_STRATEGY_MAPPING', {
        'AUTH_HEADERS': MagicMock(side_effect=EventNotDispatched)
    })
    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.tasks.logger')
    @ddt.unpack
    def test_generic_exception(self, backend_name, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name=backend_name,
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[2]
        )

        router = EventsRouter(processors=[], backend_name=backend_name)
        router.send(self.transformed_event)
        if backend_name == RouterConfiguration.CALIPER_BACKEND:
            self.assertEqual(mocked_logger.exception.call_count,
                             getattr(settings, 'EVENT_ROUTING_BACKEND_COUNTDOWN', 3) + 1)
            mocked_post.assert_not_called()
        else:
            mocked_logger.exception.assert_not_called()

    def test_with_non_dict_event(self):
        RouterConfigurationFactory.create(
            backend_name=RouterConfiguration.XAPI_BACKEND,
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[3]
        )
        router = EventsRouter(processors=[], backend_name=RouterConfiguration.XAPI_BACKEND)
        transformed_event = Statement()
        with self.assertRaises(ValueError):
            router.send(transformed_event)

    @ddt.data(
        (RouterConfiguration.AUTH_BASIC,
         None,
         'abc',
         'xyz',
         RouterConfiguration.CALIPER_BACKEND,
         'http://test1.com'
         ),
        (
            RouterConfiguration.AUTH_BEARER,
            'test_key',
            None,
            None,
            RouterConfiguration.CALIPER_BACKEND,
            'http://test2.com'
        ),
        (
            None,
            None,
            None,
            None,
            RouterConfiguration.CALIPER_BACKEND,
            'http://test3.com'
        ),
        (RouterConfiguration.AUTH_BASIC,
         None,
         'abc',
         'xyz',
         RouterConfiguration.XAPI_BACKEND,
         'http://test1.com'
         ),
        (
            RouterConfiguration.AUTH_BEARER,
            'test_key',
            None,
            None,
            RouterConfiguration.XAPI_BACKEND,
            'http://test2.com'
        ),
        (
            None,
            None,
            None,
            None,
            RouterConfiguration.XAPI_BACKEND,
            'http://test3.com'
        ),
    )
    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.utils.xapi_lrs_client.RemoteLRS')
    @ddt.unpack
    def test_successful_routing_of_event(
        self,
        auth_scheme,
        auth_key,
        username,
        password,
        backend_name,
        route_url,
        mocked_lrs,
        mocked_post,
    ):
        TieredCache.dangerous_clear_all_tiers()
        mocked_oauth_client = MagicMock()
        mocked_api_key_client = MagicMock()

        MOCKED_MAP = {
            'AUTH_HEADERS': HttpClient,
            'OAUTH2': mocked_oauth_client,
            'API_KEY': mocked_api_key_client,
            'XAPI_LRS': LrsClient,
        }
        RouterConfigurationFactory.create(
            backend_name=backend_name,
            enabled=True,
            route_url=route_url,
            auth_scheme=auth_scheme,
            auth_key=auth_key,
            username=username,
            password=password,
            configurations=ROUTER_CONFIG_FIXTURE[0]
        )

        router = EventsRouter(processors=[], backend_name=backend_name)

        with patch.dict('event_routing_backends.tasks.ROUTER_STRATEGY_MAPPING', MOCKED_MAP):
            router.send(self.transformed_event)

        overridden_event = self.transformed_event.copy()
        overridden_event['new_key'] = 'new_value'

        if backend_name == RouterConfiguration.XAPI_BACKEND:
            # test LRS Client
            mocked_lrs().save_statement.assert_has_calls([
                call(overridden_event),
            ])
        else:
            # test the HTTP client
            if auth_scheme == RouterConfiguration.AUTH_BASIC:
                mocked_post.assert_has_calls([
                    call(
                        url=route_url,
                        json=overridden_event,
                        headers={
                        },
                        auth=(username, password)
                    ),
                ])
            elif auth_scheme == RouterConfiguration.AUTH_BEARER:
                mocked_post.assert_has_calls([
                    call(
                        url=route_url,
                        json=overridden_event,
                        headers={
                            'Authorization': RouterConfiguration.AUTH_BEARER + ' ' + auth_key
                        }
                    ),
                ])
            else:
                mocked_post.assert_has_calls([
                    call(
                        url=route_url,
                        json=overridden_event,
                        headers={
                        },
                    ),
                ])

        # test mocked oauth client
        mocked_oauth_client.assert_not_called()

    def test_unsuccessful_routing_of_event(self):
        host_configurations = {
                        'url': 'http://test3.com',
                        'version': '1.0.1',
                        'auth_scheme': 'bearer',
                        'auth_key': 'key',
                    }
        client = LrsClient(**host_configurations)
        with self.assertRaises(EventNotDispatched):
            client.send(event_name='test', statement_data={})

    def test_unsuccessful_routing_of_event_http(self):
        host_configurations = {
                        'url': 'http://test4.com',
                        'auth_scheme': 'bearer',
                        'auth_key': 'key',
                    }
        client = HttpClient(**host_configurations)
        with self.assertRaises(EventNotDispatched):
            client.send(event=self.transformed_event, event_name=self.transformed_event['name'])
