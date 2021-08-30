"""
Generic router to send events to hosts.
"""
import logging

from eventtracking.processors.exceptions import EventEmissionExit

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.tasks import dispatch_event

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

            router_url = router.route_url
            for host in hosts:
                updated_event = self.overwrite_event_data(processed_event, host)
                host['host_configurations'].update({'url': router_url})
                dispatch_event.delay(
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
