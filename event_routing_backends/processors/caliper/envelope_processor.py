"""
Envelope the caliper transformed event.
"""
from datetime import datetime

from pytz import UTC

from event_routing_backends.helpers import convert_datetime_to_iso
from event_routing_backends.processors.caliper.constants import CALIPER_EVENT_CONTEXT


class CaliperEnvelopeProcessor:
    """
    Envelope the caliper transformed event.
    """
    def __init__(self, sensor_id):
        """
        Initialize the processor.
        """
        self.sensor_id = sensor_id

    def __call__(self, event):
        """
        Envelope the caliper transformed event.

        Arguments:
            event (dict):   IMS Caliper compliant event dict

        Returns:
            dict
        """
        return {
            'sensor': self.sensor_id,
            'sendTime': convert_datetime_to_iso(datetime.now(UTC)),
            'data': [event],
            'dataVersion': CALIPER_EVENT_CONTEXT
        }
