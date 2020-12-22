"""
event_routing_backends Django application initialization.
"""

from django.apps import AppConfig


class EventRoutingBackendsConfig(AppConfig):
    """
    Configuration for the event_routing_backends Django application.
    """

    name = 'event_routing_backends'

    def ready(self):
        """
        Import the signals and transformers for initialization.
        """
        super().ready()
        # pylint: disable=import-outside-toplevel, unused-import
        from event_routing_backends.processors.caliper import event_transformers as caliper_event_transformers
        from event_routing_backends.processors.xapi import event_transformers as xapi_event_transformers
