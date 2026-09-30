"""
Test plugin settings for commond, devstack and production environments
"""

from django.conf import settings
from django.test import TestCase, override_settings

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

        self.assertIn('event_transformer', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('OPTIONS', settings.EVENT_TRACKING_BACKENDS["event_transformer"])
        transformer_options = settings.EVENT_TRACKING_BACKENDS["event_transformer"]["OPTIONS"]

        self.assertEqual(
            set(
                settings.EVENT_TRACKING_BACKENDS_ALLOWED_XAPI_EVENTS +
                settings.EVENT_TRACKING_BACKENDS_ALLOWED_CALIPER_EVENTS,
            ),
            transformer_options["processors"][0]["OPTIONS"]["whitelist"]
        )

        self.assertIn("xapi", transformer_options["backends"])
        self.assertEqual(
            settings.EVENT_TRACKING_BACKENDS_ALLOWED_XAPI_EVENTS,
            transformer_options["backends"]["xapi"]["OPTIONS"]["processors"][0]["OPTIONS"]["whitelist"])

        self.assertIn("caliper", settings.EVENT_TRACKING_BACKENDS["event_transformer"]["OPTIONS"]["backends"])
        self.assertEqual(
            settings.EVENT_TRACKING_BACKENDS_ALLOWED_CALIPER_EVENTS,
            transformer_options["backends"]["caliper"]["OPTIONS"]["processors"][0]["OPTIONS"]["whitelist"])

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
        self.assertIn('event_transformer', settings.EVENT_TRACKING_BACKENDS)
        self.assertIn('xapi', settings.EVENT_TRACKING_BACKENDS["event_transformer"]["OPTIONS"]["backends"])
        self.assertIn('caliper', settings.EVENT_TRACKING_BACKENDS["event_transformer"]["OPTIONS"]["backends"])
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

    @override_settings(
        EVENT_TRACKING_BACKENDS_ALLOWED_XAPI_EVENTS=["my.event.1"],
        EVENT_TRACKING_BACKENDS_ALLOWED_CALIPER_EVENTS=["my.event.2"],
    )
    def test_settings_append_events(self):
        common_settings.plugin_settings(settings)

        self.assertGreater(len(settings.EVENT_TRACKING_BACKENDS_ALLOWED_XAPI_EVENTS), 1)
        self.assertIn("my.event.1", settings.EVENT_TRACKING_BACKENDS_ALLOWED_XAPI_EVENTS)

        self.assertGreater(len(settings.EVENT_TRACKING_BACKENDS_ALLOWED_CALIPER_EVENTS), 1)
        self.assertIn("my.event.2", settings.EVENT_TRACKING_BACKENDS_ALLOWED_CALIPER_EVENTS)
