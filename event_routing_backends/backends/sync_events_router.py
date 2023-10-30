"""
Events router to send events to hosts in sync mode.

This router is expected to be used with the event bus, which
can be configured to use this router to send events to hosts
in the same thread as it process the events.
"""
from event_routing_backends.backends.events_router import EventsRouter
from event_routing_backends.tasks import bulk_send_events, send_event


class SyncEventsRouter(EventsRouter):
    """
    Router to send events to hosts using requests library.
    """

    def dispatch_event(self, event_name, updated_event, router_type, host_configurations):
        """
        Dispatch the event to the configured router.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        send_event(None, event_name, updated_event, router_type, host_configurations)

    def dispatch_bulk_events(self, events, router_type, host_configurations):
        """
        Dispatch the a list of events to the configured router in bulk.

        Arguments:
            events (list[dict]):        list of processed event dictionaries
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        bulk_send_events(None, events, router_type, host_configurations)

    def dispatch_event_persistent(self, event_name, updated_event, router_type, host_configurations):
        """
        Dispatch the event to the configured router providing persistent storage.
        In this case, the event bus is expected to provide the persistent storage layer.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        self.dispatch_event(event_name, updated_event, router_type, host_configurations)
