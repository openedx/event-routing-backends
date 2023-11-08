"""
Test functions in event transformers not necessarily covered by the fixtures.
"""

import json

from django.test import SimpleTestCase

from event_routing_backends.processors.xapi.event_transformers.problem_interaction_events import JSONEncodedResult


class TestXAPIEventTransformers(SimpleTestCase):
    """
    These cases are covered by the fixtures, but coverage doesn't think so.
    """
    def test_jsonencodedresult_list(self):
        test_data = ["foo", "b'ar", 'test"ing', 2]
        result = JSONEncodedResult()
        result.response = test_data
        self.assertEqual(test_data, json.loads(result.response))

    def test_jsonencodedresult_not_list(self):
        test_data = "this is not a list and should fail"
        result = JSONEncodedResult()

        with self.assertRaises(ValueError):
            result.response = test_data
