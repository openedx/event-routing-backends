"""
xAPI processor for transforming and routing events.
"""
import json
from logging import getLogger

from eventtracking.processors.exceptions import EventEmissionExit

from event_routing_backends.processors.mixins.base_transformer_processor import BaseTransformerProcessorMixin
from event_routing_backends.processors.xapi import XAPI_EVENTS_ENABLED
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry

xapi_logger = getLogger('xapi_tracking')


class XApiProcessor(BaseTransformerProcessorMixin):
    """
    xAPI Processor for transforming and routing events.

    This processor first transform the event using the registered transformer
    and then route the events through the configured routers.

    Every router configured to be used MUST support the transformed event type.
    """

    registry = XApiTransformersRegistry

    def transform_event(self, event):
        """
        Transform the event into IMS xAPI format.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            dict:           transformed event

        Raises:
            Any Exception
        """
        if not XAPI_EVENTS_ENABLED.is_enabled():
            raise EventEmissionExit

        transformed_event = super().transform_event(event)

        if transformed_event:
            event_json = transformed_event.to_json()
            xapi_logger.info(event_json)
            return json.loads(event_json)

        return transformed_event
