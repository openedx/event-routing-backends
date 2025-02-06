"""
Generic router to send events to hosts.
"""
import json
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django_redis import get_redis_connection
from eventtracking.backends.logger import DateTimeJSONEncoder
from eventtracking.processors.exceptions import EventEmissionExit

from event_routing_backends.helpers import get_business_critical_events
from event_routing_backends.models import RouterConfiguration

logger = logging.getLogger(__name__)

EVENTS_ROUTER_QUEUE_FORMAT = 'events_router_queue_{}'
EVENTS_ROUTER_DEAD_QUEUE_FORMAT = 'dead_queue_{}'
EVENTS_ROUTER_LAST_SENT_FORMAT = 'last_sent_{}'


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
        self.queue_name = EVENTS_ROUTER_QUEUE_FORMAT.format(self.backend_name)
        self.dead_queue = EVENTS_ROUTER_DEAD_QUEUE_FORMAT.format(self.backend_name)
        self.last_sent_key = EVENTS_ROUTER_LAST_SENT_FORMAT.format(self.backend_name)

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

    def prepare_to_send(self, events, router_urls=None):
        """
        Prepare a list of events to be sent and create a processed, filtered batch for each router.
        If router_urls are explicitly mentioned, then only use the specified routers
        """
        routers = RouterConfiguration.get_enabled_routers(self.backend_name)
        if router_urls:
            routers = routers.filter(route_url__in=router_urls)

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

                processed_events = self.process_event(event)
            except (EventEmissionExit, ValueError):
                logger.error(
                    'Could not process edx event "%s" for backend %s\'s router',
                    event_name,
                    self.backend_name,
                    exc_info=True
                )
                continue

            logger.debug(
                'Successfully processed edx event "%s" for router with backend %s. Processed events: %s',
                event_name,
                self.backend_name,
                processed_events
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

                    if processed_events and router_pk not in route_events:
                        route_events[router_pk] = []

                    for processed_event in processed_events:
                        updated_event = self.overwrite_event_data(processed_event, host, event_name)
                        is_business_critical = event_name in business_critical_events
                        route_events[router_pk].append((event_name, updated_event, host, is_business_critical))

        return route_events

    def get_failed_events(self, batch_size):
        """
        Get failed events from the dead queue.
        """
        redis = get_redis_connection()
        failed_events = redis.rpop(self.dead_queue, batch_size)
        if not failed_events:
            return []
        return [json.loads(event.decode('utf-8')) for event in failed_events]

    def bulk_send(self, events, router_urls=None):
        """
        Send the event to configured routers after processing it.

        Event is processed through the configured processors. A router config
        object matching the backend_name and other match params is used to get
        the list of hosts to which the event is required to be delivered to.

        Arguments:
            events (list[dict]): list of original event dictionaries
        """
        event_routes = self.prepare_to_send(events, router_urls)

        for events_for_route in event_routes.values():
            prepared_events = []
            host = None
            ids = set()
            for _, updated_event, host, _ in events_for_route:
                if updated_event["id"] in ids:
                    logger.info(f"Found duplicated event {updated_event['id']}")
                    continue
                prepared_events.append(updated_event)
                ids.add(updated_event["id"])

            if prepared_events:  # pragma: no cover
                self.dispatch_bulk_events(
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
        if settings.EVENT_ROUTING_BACKEND_BATCHING_ENABLED:
            redis = get_redis_connection()
            batch = self.queue_event(redis, event)
            if not batch:
                return

            try:
                redis.set(self.last_sent_key, datetime.now().isoformat())
                self.bulk_send([json.loads(queued_event.decode('utf-8')) for queued_event in batch])
            except Exception:  # pylint: disable=broad-except
                logger.exception(
                    'Exception occurred while trying to bulk dispatch {} events.'.format(
                        len(batch)
                    ),
                    exc_info=True
                )
                logger.info(f'Pushing failed events to the dead queue: {self.dead_queue}')
                redis.lpush(self.dead_queue, *batch)
            return

        event_routes = self.prepare_to_send([event])
        for events_for_route in event_routes.values():
            for event_name, updated_event, host, is_business_critical in events_for_route:
                if is_business_critical:
                    self.dispatch_event_persistent(
                        event_name,
                        updated_event,
                        host['router_type'],
                        host['host_configurations'],
                    )
                else:
                    self.dispatch_event(
                        event_name,
                        updated_event,
                        host['router_type'],
                        host['host_configurations'],
                    )

    def queue_event(self, redis, event):
        """
        Queue the event to be sent to configured routers.

        """
        if isinstance(event["timestamp"], datetime):
            event["timestamp"] = event["timestamp"].isoformat()
        queue_size = redis.lpush(self.queue_name, json.dumps(event, cls=DateTimeJSONEncoder))
        logger.info(f'Event {event["name"]} has been queued for batching. Queue size: {queue_size}')

        if queue_size >= settings.EVENT_ROUTING_BACKEND_BATCH_SIZE or self.time_to_send(redis):
            batch = redis.rpop(self.queue_name, queue_size)

            orig_size = len(batch)
            # Deduplicate list, in some misconfigured cases tracking events can be emitted to the
            # bus twice, causing them to be processed twice, which LRSs will reject.
            # See: https://github.com/openedx/event-routing-backends/issues/410
            batch = [i for n, i in enumerate(batch) if i not in batch[n + 1:]]
            final_size = len(batch)

            if final_size != orig_size:  # pragma: no cover
                logger.warning(f"{orig_size - final_size} duplicate events in event-routing-backends batch queue! "
                               f"This is a likely due to misconfiguration of EVENT_TRACKING_BACKENDS.")
            return batch

        return None

    def time_to_send(self, redis):
        """
        Check if it is time to send the batched events.
        """
        last_sent = redis.get(self.last_sent_key)
        if not last_sent:
            return True
        time_passed = (datetime.now() - datetime.fromisoformat(last_sent.decode('utf-8')))
        ready = time_passed > timedelta(seconds=settings.EVENT_ROUTING_BACKEND_BATCH_INTERVAL)

        return ready

    def process_event(self, event):
        """
        Process the event through this router's processors.

        This single event may produce multiple processed events, and so we return a list of events here.

        Arguments:
            event (dict):      Event to be processed

        Returns
            list of ANY
        """
        events = [event.copy()]
        for processor in self.processors:
            events = processor(events)

        return events

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

    def dispatch_event(self, event_name, updated_event, router_type, host_configurations):
        """
        Dispatch the event to the configured router.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        raise NotImplementedError('dispatch_event is not implemented')

    def dispatch_bulk_events(self, events, router_type, host_configurations):
        """
        Dispatch the a list of events to the configured router in bulk.

        Arguments:
            events (list[dict]):        list of processed event dictionaries
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        raise NotImplementedError('dispatch_bulk_events is not implemented')

    def dispatch_event_persistent(self, event_name, updated_event, router_type, host_configurations):
        """
        Dispatch the event to the configured router providing persistent storage.

        Arguments:
            event_name (str):           name of the original event.
            updated_event (dict):       processed event dictionary
            router_type (str):          type of the router
            host_configurations (dict): host configurations dict
        """
        raise NotImplementedError('dispatch_event_persistent is not implemented')
