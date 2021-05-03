"""
Generic router to send events to hosts.
"""
import logging

from eventtracking.processors.exceptions import EventEmissionExit

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.utils.http_client import HttpClient
from event_routing_backends.utils.xapi_lrs_client import LrsClient

logger = logging.getLogger(__name__)

ROUTER_STRATEGY_MAPPING = {
    'AUTH_HEADERS': HttpClient,
    'XAPI_LRS': LrsClient,
}


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

    def _copy(self, event):
        """
        Copy the event to avoid mutation.

        Currently supports only `dict` type events.
        """
        if isinstance(event, dict):
            return event.copy()
        else:
            raise ValueError('Expected event as dict but {type} was given.'.format(type=type(event)))

    def send(self, event):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name is used to get the list of hosts to
        which the event is required to be delivered to.
        Then a client as per the router configurations will be used to deliver the
        event.

        Arguments:
            original_event (dict):      original event dictionary
            transformed_event (dict):   transformed event dictionary
        """
        try:
            logger.debug(
                'Processing event %s for router with backend %s',
                event,
                self.backend_name
            )

            processed_event = self.process_event(event)
        except EventEmissionExit:
            logger.error(
                'Could not process event %s for backend %s\'s router',
                event,
                self.backend_name,
                exc_info=True
            )
            return

        logger.debug('Successfully processed event %s for router with backend %s',
                     event, self.backend_name)

        routers = RouterConfiguration.get_enabled_routers(self.backend_name)

        if not routers:
            logger.error('Could not find an enabled router configurations for backend %s', self.backend_name)
            return

        for router in routers:
            hosts = router.get_allowed_hosts(event)

            if not hosts:
                logger.info(
                    'Event %s is not allowed to be sent to any host for router with backend "%s"',
                    event, self.backend_name
                )
                return

            for host in hosts:
                updated_event = self.overwrite_event_data(processed_event, host)

                self.dispatch_event(
                    event,
                    updated_event,
                    host['router_type'],
                    host['host_configurations']
                )

    def process_event(self, event):
        """
        Process the event through this router's processors.

        Arguments:
            event (dict):      Event to be processed

        Returns
            dict
        """
        event = self._copy(event)
        for processor in self.processors:
            event = processor(event)

        return event

    def overwrite_event_data(self, event, host):
        """
        Overwrite/Add values in the event.

        If there is `override_args` key in the host configurations,
        add those keys to the event and overwrite the existing values (if any).

        Arguments:
            event (dict):   Event in which values are to be added/overwritten
            host (dict):    Host configurations dict.

        Returns:
            dict
        """
        if 'override_args' in host and isinstance(event, dict):
            event = self._copy(event)
            event.update(host['override_args'])
            logger.debug('Overwriting event with values {}'.format(host['override_args']))
        return event

    def dispatch_event(self, event_name, event, router_type, host_config):
        """
        Send event to configured client.

        Arguments:
            event_name (str)    : name of the original event
            event (dict)        : event dictionary to be delivered.
            router_type (str)   : decides the client to use for sending the event
            host_config (dict)  : contains configurations for the host.
        """
        logger.debug(
            'Routing event "%s" for router type "%s"',
            event_name,
            router_type
        )

        try:
            client_class = ROUTER_STRATEGY_MAPPING[router_type]
        except KeyError:
            logger.error('Unsupported routing strategy detected: {}'.format(router_type))
            return

        try:
            client = client_class(**host_config)
            client.send(event)
            logger.debug(
                'Successfully dispatched event "{}" using client strategy "{}"'.format(
                    event_name,
                    router_type
                )
            )

        except Exception:   # pylint: disable=broad-except
            logger.exception(
                'Exception occured while trying to dispatch event "{}"'.format(
                    event_name,
                ),
                exc_info=True
            )
