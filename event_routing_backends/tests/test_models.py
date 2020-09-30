"""
Test the django models
"""
import ddt
from django.test import TestCase

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
            backend_name='first'
        )

        second_router = RouterConfigurationFactory(
            configurations='{}',
            enabled=False,
            backend_name='second'
        )

        self.assertEqual(RouterConfiguration.get_enabled_router('first'), first_router)
        self.assertEqual(RouterConfiguration.get_enabled_router('second'), None)

        second_router.enabled = True
        second_router.save()

        self.assertEqual(RouterConfiguration.get_enabled_router('second'), second_router)

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
            backend_name='first'
        )

        hosts = router.get_allowed_hosts(original_event)
        self.assertEqual(config_fixture[:1], hosts)
