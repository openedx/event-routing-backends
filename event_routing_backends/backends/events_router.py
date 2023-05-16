"""
Generic router to send events to hosts.
"""
import logging

from eventtracking.processors.exceptions import EventEmissionExit

from event_routing_backends.helpers import get_business_critical_events
from event_routing_backends.models import RouterConfiguration
from event_routing_backends.tasks import dispatch_bulk_events, dispatch_event, dispatch_event_persistent

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

    def configure_host(self, host, router):
        """
        Create host_configurations for the given host and router.
        """
        host['host_configurations'] = {}
        host['host_configurations'].update({'url': router.route_url})
        host['host_configurations'].update({'auth_scheme': router.auth_scheme})

        if router.auth_scheme == RouterConfiguration.AUTH_BASIC:
            host['host_configurations'].update({'username': router.username})
            host['host_configurations'].update({'password': router.password})
        elif router.auth_scheme == RouterConfiguration.AUTH_BEARER:
            host['host_configurations'].update({'auth_key': router.auth_key})

        if router.backend_name == RouterConfiguration.CALIPER_BACKEND:
            host.update({'router_type': 'AUTH_HEADERS'})
            if 'headers' in host:
                host['host_configurations'].update({'headers': host['headers']})
        elif router.backend_name == RouterConfiguration.XAPI_BACKEND:
            host.update({'router_type': 'XAPI_LRS'})
        else:
            host.update({'router_type': 'INVALID_TYPE'})

        return host

    def prepare_to_send(self, events):
        """
        Prepare a list of events to be sent and create a processed, filtered batch for each router.
        """
        routers = RouterConfiguration.get_enabled_routers(self.backend_name)
        business_critical_events = get_business_critical_events()
        route_events = {}

        # We continue even without routers here to allow logging of statements to happen.
        # If operators do not wish to log and have no enabled routers they should set XAPI_EVENTS_ENABLED
        # or CALIPER_EVENTS_ENABLED to false.
        if not routers:
            logger.debug('Could not find any enabled router configuration for backend %s', self.backend_name)
            routers = []

        for event in events:
            try:
                event_name = event['name']
            except TypeError as exc:
                raise ValueError('Expected event as dict but {type} was given.'.format(type=type(event))) from exc

            try:
                logger.debug(
                    'Processing edx event "{}" for router with backend {}'.format(event_name, self.backend_name)
                )

                processed_event = self.process_event(event)
            except (EventEmissionExit, ValueError):
                logger.error(
                    'Could not process edx event "%s" for backend %s\'s router',
                    event_name,
                    self.backend_name,
                    exc_info=True
                )
                continue

            logger.debug(
                'Successfully processed edx event "%s" for router with backend %s. Processed event: %s',
                event_name,
                self.backend_name,
                processed_event
            )

            for router in routers:
                host = router.get_allowed_host(event)
                router_pk = router.pk

                if not host:
                    logger.info(
                        'Event %s is not allowed to be sent to any host for router ID %s with backend "%s"',
                        event_name, router_pk, self.backend_name
                    )
                else:
                    host = self.configure_host(host, router)
                    updated_event = self.overwrite_event_data(processed_event, host, event_name)
                    is_business_critical = event_name in business_critical_events
                    if router_pk not in route_events:
                        route_events[router_pk] = [(event_name, updated_event, host, is_business_critical),]
                    else:
                        route_events[router_pk].append((event_name, updated_event, host, is_business_critical))

        return route_events

    def bulk_send(self, events):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name and other match params is used to get
        the list of hosts to which the event is required to be delivered to.

        Arguments:
            events (list[dict]): list of original event dictionaries
        """
        event_routes = self.prepare_to_send(events)

        for events_for_route in event_routes.values():
            prepared_events = []
            host = None
            for _, updated_event, host, _ in events_for_route:
                prepared_events.append(updated_event)

            if prepared_events:  # pragma: no cover
                dispatch_bulk_events.delay(
                    prepared_events,
                    host['router_type'],
                    host['host_configurations']
                )

    def send(self, event):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name and other match params is used to get
        the list of hosts to which the event is required to be delivered to.

        Arguments:
            event (dict): the original event dictionary
        """
        event_routes = self.prepare_to_send([event])

        for events_for_route in event_routes.values():
            for event_name, updated_event, host, is_business_critical in events_for_route:
                if is_business_critical:
                    dispatch_event_persistent.delay(
                        event_name,
                        updated_event,
                        host['router_type'],
                        host['host_configurations']
                    )
                else:
                    dispatch_event.delay(
                        event_name,
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
        event = event.copy()
        for processor in self.processors:
            event = processor(event)

        return event

    def overwrite_event_data(self, event, host, event_name):
        """
        Overwrite/Add values in the event.

        If there is `override_args` key in the host configurations,
        add those keys to the event and overwrite the existing values (if any).

        Arguments:
            event (dict):       Event in which values are to be added/overwritten
            host (dict):        Host configurations dict.
            event_name (str):   name of the original event.

        Returns:
            dict
        """
        if 'override_args' in host and isinstance(event, dict):
            event = event.copy()
            event.update(host['override_args'])
            logger.debug('Overwriting processed version of edx event "{}" with values {}'.format(
                event_name,
                host['override_args']
            ))
        return event
