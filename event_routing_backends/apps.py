"""
event_routing_backends Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins import PluginSettings

from .constants import ProjectType, SettingsType


class EventRoutingBackendsConfig(AppConfig):
    """
    Configuration for the event_routing_backends Django application.
    """

    name = 'event_routing_backends'
    verbose_name = "Event Routing Backends"

    plugin_app = {
            PluginSettings.CONFIG: {
                ProjectType.LMS: {
                    SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: 'settings.production'},
                    SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: 'settings.common'},
                    SettingsType.DEVSTACK: {PluginSettings.RELATIVE_PATH: 'settings.devstack'},
                },
                ProjectType.CMS: {
                    SettingsType.PRODUCTION: {PluginSettings.RELATIVE_PATH: 'settings.production'},
                    SettingsType.COMMON: {PluginSettings.RELATIVE_PATH: 'settings.common'},
                    SettingsType.DEVSTACK: {PluginSettings.RELATIVE_PATH: 'settings.devstack'},
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
