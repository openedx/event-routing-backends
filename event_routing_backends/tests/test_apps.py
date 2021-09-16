"""
Test password policy settings
"""

from django.conf import settings
from django.test import TestCase, override_settings

import event_routing_backends as event_routing_backends
from event_routing_backends.apps import EventRoutingBackendsConfig


class TestApps(TestCase):
    """
    Tests plugin config
    """

    @override_settings(
        CALIPER_EVENTS_ENABLED=False,
        XAPI_EVENTS_ENABLED=False
    )
    def test_settings_misconfiguration(self, ):
        """
        Test that we gracefully handle configurations
        """
        app = EventRoutingBackendsConfig('event_routing_backends', event_routing_backends)
        app.ready()
        config = settings.EVENT_TRACKING_BACKENDS

        assert settings.CALIPER_EVENTS_ENABLED is True
        assert settings.CALIPER_EVENTS_ENABLED is True

        assert isinstance(config, dict)
