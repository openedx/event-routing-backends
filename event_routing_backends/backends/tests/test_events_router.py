"""
Test the EventsRouter
"""
from unittest.mock import MagicMock, call, patch, sentinel

from django.test import TestCase
from edx_django_utils.cache.utils import TieredCache
from eventtracking.processors.exceptions import EventEmissionExit
from tincan.statement import Statement

from event_routing_backends.backends.events_router import EventsRouter
from event_routing_backends.tests.factories import RouterConfigurationFactory
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

ROUTER_CONFIG_FIXTURE = [
    {
        'router_type': 'AUTH_HEADERS',
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'url': 'http://test1.com',
            'headers': {},
            'auth_scheme': 'Bearer',
            'auth_key': 'test_key'
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'router_type': 'AUTH_HEADERS',
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'url': 'http://test1.com',
            'headers': {},
        },
        'override_args': {
            'new_key': 'new_value'
        }
    },
    {
        'router_type': 'OAUTH2',
        'match_params': {
            'non_existing.id.value': 'test'
        },
        'host_configurations': {
            'url': 'http://test2.com',
            'client_id': 'id',
            'client_secret': 'secret'
        },
        'override_args': {}
    },
    {
        'router_type': 'API_KEY',
        'match_params': {
            'data.key': 'value'
        },
        'host_configurations': {
            'url': 'http://test3.com',
            'api_key': 'test_key'
        }
    },
    {
        'router_type': 'XAPI_LRS',
        'match_params': {},
        'host_configurations': {
            'url': 'http://test3.com',
            'version': '1.0.1'
        }
    },
    {
        'router_type': 'XAPI_LRS',
        'match_params': {},
        'host_configurations': {
            'url': 'http://test3.com',
            'version': '1.0.1',
            'auth_scheme': 'bearer',
            'auth_key': 'key',
        }
    }
]


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
            'Could not process event %s for backend %s\'s router',
            self.transformed_event,
            'test',
            exc_info=True
        ), mocked_logger.error.mock_calls)

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_no_router_configurations_available(self, mocked_logger, mocked_post):
        router = EventsRouter(processors=[], backend_name='test')
        router.send(self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call('Could not find an enabled router configurations for backend %s', 'test'),
            mocked_logger.error.mock_calls
        )

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_unsupported_routing_strategy(self, mocked_logger, mocked_post):
        configurations = ROUTER_CONFIG_FIXTURE[0:1].copy()
        configurations[0]['router_type'] = 'INVALID_TYPE'

        RouterConfigurationFactory.create(
            backend_name='test_backend',
            enabled=True,
            route_url='http://test3.com',
            configurations=configurations
        )

        router = EventsRouter(processors=[], backend_name='test_backend')
        TieredCache.dangerous_clear_all_tiers()
        router.send(self.transformed_event)

        mocked_logger.error.assert_called_once_with('Unsupported routing strategy detected: INVALID_TYPE')
        mocked_post.assert_not_called()

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_with_no_available_hosts(self, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name='test_backend',
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[1:1]
        )

        router = EventsRouter(processors=[], backend_name='test_backend')
        TieredCache.dangerous_clear_all_tiers()
        router.send(self.transformed_event)

        mocked_post.assert_not_called()

        self.assertIn(
            call(
                'Event %s is not allowed to be sent to any host for router with backend "%s"',
                self.transformed_event, 'test_backend'
            ),
            mocked_logger.info.mock_calls
        )

    @patch.dict('event_routing_backends.backends.events_router.ROUTER_STRATEGY_MAPPING', {
        'AUTH_HEADERS': MagicMock(side_effect=Exception)
    })
    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.backends.events_router.logger')
    def test_generic_exception(self, mocked_logger, mocked_post):
        RouterConfigurationFactory.create(
            backend_name='test_backend',
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[0:1]
        )

        router = EventsRouter(processors=[], backend_name='test_backend')
        router.send(self.transformed_event)

        mocked_logger.exception.assert_called_once()
        mocked_post.assert_not_called()

    def test_with_non_dict_event(self):
        RouterConfigurationFactory.create(
            backend_name='test_routing',
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE[4:5]
        )
        router = EventsRouter(processors=[], backend_name='test_routing')
        transformed_event = Statement()
        with self.assertRaises(ValueError):
            router.send(transformed_event)

    @patch('event_routing_backends.utils.http_client.requests.post')
    @patch('event_routing_backends.utils.xapi_lrs_client.RemoteLRS')
    def test_successful_routing_of_event(self, mocked_lrs, mocked_post):
        mocked_oauth_client = MagicMock()
        mocked_api_key_client = MagicMock()

        MOCKED_MAP = {
            'AUTH_HEADERS': HttpClient,
            'OAUTH2': mocked_oauth_client,
            'API_KEY': mocked_api_key_client,
            'XAPI_LRS': LrsClient,
        }

        RouterConfigurationFactory.create(
            backend_name='test_routing',
            enabled=True,
            route_url='http://test3.com',
            configurations=ROUTER_CONFIG_FIXTURE
        )

        router = EventsRouter(processors=[], backend_name='test_routing')

        with patch.dict('event_routing_backends.backends.events_router.ROUTER_STRATEGY_MAPPING', MOCKED_MAP):
            router.send(self.transformed_event)

        # test the HTTP client
        overridden_event = self.transformed_event.copy()
        overridden_event['new_key'] = 'new_value'

        mocked_post.assert_has_calls([
            call(
                url=ROUTER_CONFIG_FIXTURE[0]['host_configurations']['url'],
                json=overridden_event,
                headers={
                    'Authorization': 'Bearer test_key'
                }
            ),
        ])
        # test LRS Client
        mocked_lrs().save_statement.assert_has_calls([
            call(self.transformed_event),
            call(self.transformed_event),
        ])

        # test mocked api key client
        mocked_api_key_client.assert_has_calls([
            call(**ROUTER_CONFIG_FIXTURE[3]['host_configurations']),
            call().send(self.transformed_event)
        ])

        # test mocked oauth client
        mocked_oauth_client.assert_not_called()
