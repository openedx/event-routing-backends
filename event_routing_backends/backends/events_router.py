"""
Generic router to send events to hosts.
"""
import logging

from event_routing_backends.tasks import process_event

logger = logging.getLogger(__name__)


class EventsRouter:
    """
    Router to send events to hosts using requests library.
    """

    def __init__(self, processors=None, backend_name=None):
        """
        Initialize the router.

        Arguments:
            processors (list):   list of processor instances
            backend_name (str):  name of the router backend
        """
        self.processors = processors if processors else []
        self.backend_name = backend_name

    def send(self, event):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name is used to get the list of hosts to
        which the event is required to be delivered to.
        Then a client as per the router configurations will be used to deliver the
        event.

        Arguments:
            event (dict):      original event dictionary
        """
        process_event.delay(self.backend_name, event, self.processors)
