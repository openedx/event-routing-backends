"""
Generic router to send events to hosts.
"""
from event_routing_backends.tasks import send_event, bulk_send_events
from event_routing_backends.backends.events_router import EventsRouter

class SyncEventsRouter(EventsRouter):
    """
    Router to send events to hosts via celery using requests library.
    """

    def dispatch_event(self, event_name, event, router_type, host_configurations):
        """
        Dispatch the event to the configured router.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        send_event(None, event_name, event, router_type, host_configurations)

    def dispatch_bulk_events(self, events, router_type, host_configurations):
        """
        Dispatch the a list of events to the configured router in bulk.

        Arguments:
            events (list[dict]):        list of processed event dictionaries
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        bulk_send_events(None, events, router_type, host_configurations)

    def dispatch_event_persistent(self, event_name, event, router_type, host_configurations):
        """
        Dispatch the event to the configured router providing persistent storage.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        self.dispatch_event(event_name, event, router_type, host_configurations)
