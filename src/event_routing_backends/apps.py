"""
event_routing_backends Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins import PluginSettings


class EventRoutingBackendsConfig(AppConfig):
    """
    Configuration for the event_routing_backends Django application.
    """

    name = 'event_routing_backends'
    verbose_name = "Event Routing Backends"

    plugin_app = {
        PluginSettings.CONFIG: {
            'lms.djangoapp': {
                'production': {PluginSettings.RELATIVE_PATH: 'settings.production'},
                'common': {PluginSettings.RELATIVE_PATH: 'settings.common'},
                'devstack': {PluginSettings.RELATIVE_PATH: 'settings.devstack'},
            },
            'cms.djangoapp': {
                'production': {PluginSettings.RELATIVE_PATH: 'settings.production'},
                'common': {PluginSettings.RELATIVE_PATH: 'settings.common'},
                'devstack': {PluginSettings.RELATIVE_PATH: 'settings.devstack'},
            }
        }
    }

    def ready(self):
        """
        Import the signals and transformers for initialization.
        """
        super().ready()
        # pylint: disable=import-outside-toplevel, unused-import
        from event_routing_backends.processors.caliper import event_transformers as caliper_event_transformers
        from event_routing_backends.processors.xapi import event_transformers as xapi_event_transformers
