"""
Events router to send events to hosts via celery.

This events router will trigger a celery task to send the events to the
configured hosts.
"""
from event_routing_backends.backends.events_router import EventsRouter
from event_routing_backends.tasks import dispatch_bulk_events, dispatch_event, dispatch_event_persistent


class AsyncEventsRouter(EventsRouter):
    """
    Router to send events to hosts via celery using requests library.
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
        dispatch_event.delay(event_name, updated_event, router_type, host_configurations)

    def dispatch_bulk_events(self, events, router_type, host_configurations):
        """
        Dispatch the a list of events to the configured router in bulk.

        Arguments:
            events (list[dict]):        list of processed event dictionaries
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        dispatch_bulk_events.delay(events, router_type, host_configurations)

    def dispatch_event_persistent(self, event_name, updated_event, router_type, host_configurations):
        """
        Dispatch the event to the configured router providing persistent storage.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        dispatch_event_persistent.delay(event_name, updated_event, router_type, host_configurations)
