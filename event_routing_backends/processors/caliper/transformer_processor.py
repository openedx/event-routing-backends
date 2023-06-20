"""
Caliper processor for transforming and routing events.
"""
import json
from logging import getLogger

from eventtracking.processors.exceptions import NoBackendEnabled

from event_routing_backends.processors.caliper import CALIPER_EVENT_LOGGING_ENABLED, CALIPER_EVENTS_ENABLED
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.mixins.base_transformer_processor import BaseTransformerProcessorMixin

logger = getLogger(__name__)
caliper_logger = getLogger('caliper_tracking')


class CaliperProcessor(BaseTransformerProcessorMixin):
    """
    Caliper Processor for transforming and routing events.

    This processor first transform the event using the registered transformer
    and then route the events through the configured routers.

    Every router configured to be used MUST support the transformed event type.
    """

    registry = CaliperTransformersRegistry

    def transform_event(self, event):
        """
        Transform the event into IMS Caliper format.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            dict:           transformed event

        Raises:
            Any Exception
        """
        if not CALIPER_EVENTS_ENABLED.is_enabled():
            raise NoBackendEnabled

        transformed_event = super().transform_event(event)

        if transformed_event:
            json_event = json.dumps(transformed_event)

            if CALIPER_EVENT_LOGGING_ENABLED.is_enabled():
                caliper_logger.info(json_event)

            logger.debug('Caliper version of edx event "{}" is: {}'.format(
                event["name"],
                json_event
            ))

        return transformed_event
