"""
Test the django models
"""
import ddt
from django.test import TestCase
from edx_django_utils.cache.utils import TieredCache

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.tests.factories import RouterConfigurationFactory


@ddt.ddt
class TestRouterConfiguration(TestCase):
    """
    Test `RouterConfiguration` model
    """

    def test_str_method(self):
        self.assertIsNotNone(str(RouterConfiguration()))

    def test_enabled_router_is_returned(self):
        first_router = RouterConfigurationFactory(
            configurations='{}',
            enabled=True,
            route_url='http://test2.com',
            backend_name='first'
        )
        second_router = RouterConfigurationFactory(
            configurations='{}',
            enabled=False,
            route_url='http://test3.com',
            backend_name='second'
        )
        self.assertEqual(RouterConfiguration.get_enabled_routers('first')[0], first_router)
        self.assertEqual(RouterConfiguration.get_enabled_routers('second'), None)

        second_router.enabled = True
        second_router.save()
        TieredCache.dangerous_clear_all_tiers()
        self.assertEqual(RouterConfiguration.get_enabled_routers('second')[0], second_router)

    def test_allowed_hosts(self):
        config_fixture = [
            {
                'match_params': {
                    'context.org_id': 'test'
                },
                'host_configurations': {
                    'url': 'http://test1.com',
                    'headers': {
                        'authorization': 'Token test'
                    }
                }
            },
            {
                'match_params': {
                    'non_existing.id.value': 'test'
                },
                'host_configurations': {
                    'url': 'http://test2.com',
                    'headers': {
                        'authorization': 'Token test'
                    }
                }
            }
        ]

        original_event = {
            'context': {
                'org_id': 'test'
            },
            'data': {
                'id': 'test_id'
            }
        }

        router = RouterConfigurationFactory(
            configurations=config_fixture,
            enabled=True,
            route_url='http://test3.com',
            backend_name='first'
        )

        hosts = router.get_allowed_hosts(original_event)
        self.assertEqual(config_fixture[:1], hosts)

    def test_model_cache(self):
        test_cache_router = RouterConfigurationFactory(
            configurations='{}',
            enabled=True,
            route_url='http://test2.com',
            backend_name='test_cache'
        )
        self.assertEqual(RouterConfiguration.get_enabled_routers('test_cache')[0], test_cache_router)

        test_cache_router.route_url = 'http://test3.com'
        test_cache_router.save()

        self.assertNotEqual(RouterConfiguration.get_enabled_routers('test_cache')[0], test_cache_router)

    def test_multiple_routers_of_backend(self):
        backend_name = 'multiple_routers_test'
        test_cache_router = RouterConfigurationFactory(
            configurations='{}',
            enabled=True,
            route_url='http://test2.com',
            backend_name=backend_name
        )
        test_cache_router1 = RouterConfigurationFactory(
            configurations='{}',
            enabled=True,
            route_url='http://test1.com',
            backend_name=backend_name
        )

        self.assertEqual(list(RouterConfiguration.get_enabled_routers(backend_name)),
                         [test_cache_router1, test_cache_router])

    def test_empty_backend(self):
        self.assertEqual(RouterConfiguration.get_enabled_routers(''), None)
