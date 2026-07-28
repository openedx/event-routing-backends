"""
Test the django models
"""
import ddt
from django.test import TestCase
from edx_django_utils.cache.utils import TieredCache

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.tests.factories import RouterConfigurationFactory
from event_routing_backends.tests.test_mixin import RouterTestMixin

ROUTER_CONFIG_FIXTURE = [
            {
                'match_params': {
                    'context.org_id': 'abc',
                    'name': None
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
                    'context.org_id': 'test',
                    'name': ['problem_check', 'showanswer', 'stop_video']
                },
                'host_configurations': {
                    'url': 'http://test1.com',
                    'headers': {
                        'authorization': 'Token test'
                    }
                }
            }
        ]


@ddt.ddt
class TestRouterConfiguration(TestCase, RouterTestMixin):
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

    @ddt.data(
        ({'context.org_id': 'test'}, True),
        ({'non_existing.id.value': 'test'}, False),
        ({'context.org_id': 'abc', 'name': None}, False),
        ({'context.org_id': 'test', 'name': ['problem_check', 'showanswer', 'stop_video']}, True),
        ({'context.org_id': 'test', 'name': [None]}, False),
        ({'context.org_id': 'abc', 'name': 'problem_check'}, False),
        ({'context.org_id': 'test', 'name': 'problem_check'}, True),
        ({"course_id": r"^.*course-v.:edX\+.*\+2021.*$", "name": "problem_check"}, True),
        ({'context.org_id': 'test', "name": ["^problem.*", "video"]}, True),
    )
    @ddt.unpack
    def test_allowed_hosts(self, match_params, found):
        config_fixture = {
                'match_params': match_params,
                'host_configurations': {
                    'url': 'http://test1.com',
                    'headers': {
                        'authorization': 'Token test'
                    }
                }
            }

        original_event = {
            'course_id': 'course-v1:edX+E2E+2021+course',
            'name': 'problem_check',
            'context': {
                'org_id': 'test'
            },
            'data': {
                'id': 'test_id'
            }
        }
        router = self.create_router_configuration(config_fixture, 'first')

        host = router.get_allowed_host(original_event)
        if found:
            self.assertEqual(config_fixture, host)
        else:
            self.assertEqual(None, host)

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

    def test_empty_configurations(self):
        router = self.create_router_configuration(None, 'first')
        host = router.get_allowed_host({})
        self.assertEqual(host, {'host_configurations': {}})
