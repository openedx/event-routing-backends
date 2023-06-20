"""
Test plugin settings for commond, devstack and production environments
"""

from django.conf import settings
from django.test import TestCase

from event_routing_backends.settings import common as common_settings
from event_routing_backends.settings import devstack as devstack_settings
from event_routing_backends.settings import production as production_setttings


class TestPluginSettings(TestCase):
    """
    Tests plugin settings
    """

    def test_common_settings(self):
        """
        Test common settings
        """
        common_settings.plugin_settings(settings)
        self.assertIn('xapi', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('caliper', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('edx.course.enrollment.activated', settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS)
        self.assertFalse(settings.CALIPER_EVENTS_ENABLED)
        self.assertFalse(settings.CALIPER_EVENT_LOGGING_ENABLED)
        self.assertTrue(settings.XAPI_EVENTS_ENABLED)
        self.assertTrue(settings.XAPI_EVENT_LOGGING_ENABLED)

    def test_devstack_settings(self):
        """
        Test devstack settings
        """
        devstack_settings.plugin_settings(settings)
        self.assertIn('xapi', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('caliper', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('edx.course.enrollment.deactivated', settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS)
        self.assertFalse(settings.CALIPER_EVENTS_ENABLED)
        self.assertFalse(settings.CALIPER_EVENT_LOGGING_ENABLED)
        self.assertTrue(settings.XAPI_EVENTS_ENABLED)
        self.assertTrue(settings.XAPI_EVENT_LOGGING_ENABLED)

    def test_production_settings(self):
        """
        Test production settings
        """
        settings.ENV_TOKENS = {
            'EVENT_TRACKING_BACKENDS': None,
            'CALIPER_EVENTS_ENABLED': False,
            'CALIPER_EVENT_LOGGING_ENABLED': True,
            'XAPI_EVENTS_ENABLED': False,
            'XAPI_EVENT_LOGGING_ENABLED': True,
            'EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS': [],
        }
        production_setttings.plugin_settings(settings)
        self.assertIsNone(settings.EVENT_TRACKING_BACKENDS)
        self.assertFalse(bool(settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS))
        self.assertFalse(settings.CALIPER_EVENTS_ENABLED)
        self.assertTrue(settings.CALIPER_EVENT_LOGGING_ENABLED)
        self.assertFalse(settings.XAPI_EVENTS_ENABLED)
        self.assertTrue(settings.XAPI_EVENT_LOGGING_ENABLED)
