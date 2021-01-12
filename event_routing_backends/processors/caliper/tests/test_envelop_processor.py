"""
Test the CaliperEnvelopProcessor.
"""
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, sentinel

from pytz import UTC

from event_routing_backends.helpers import convert_datetime_to_iso
from event_routing_backends.processors.caliper.constants import CALIPER_EVENT_CONTEXT
from event_routing_backends.processors.caliper.envelop_processor import CaliperEnvelopProcessor

FROZEN_TIME = datetime(2013, 10, 3, 8, 24, 55, tzinfo=UTC)


class TestCaliperEnvelopProcessor(TestCase):
    """
    Test the CaliperEnvelopProcessor.
    """

    def setUp(self):
        super().setUp()
        self.sample_event = {
            'name': str(sentinel.name)
        }
        self.sensor_id = 'http://test.sensor.com'

    @patch('event_routing_backends.processors.caliper.envelop_processor.datetime')
    def test_caliper_envelop_processor(self, mocked_datetime):
        mocked_datetime.now.return_value = FROZEN_TIME

        result = CaliperEnvelopProcessor(sensor_id=self.sensor_id)(self.sample_event)
        self.assertEqual(result, {
            'sensor': self.sensor_id,
            'sendTime': convert_datetime_to_iso(str(FROZEN_TIME)),
            'data': [self.sample_event],
            'dataVersion': CALIPER_EVENT_CONTEXT
        })
