"""
Test the TransformerRegistry
"""
from unittest.mock import MagicMock

import ddt
from django.test import TestCase

from event_routing_backends.processors.transformer_utils.registry import TransformerRegistry


@ddt.ddt
class TestTransformerRegistry(TestCase):
    """
    Test the TransformerRegistry.
    """

    def test_validate_mapping_exists(self):
        class WithoutRegistry(TransformerRegistry):
            pass

        with self.assertRaises(AttributeError):
            WithoutRegistry.register('test.key')(MagicMock())

    def test_override_register(self):
        mocked_transformer = MagicMock()
        mocked_transformer2 = MagicMock()

        TransformerRegistry.register('test.key')(mocked_transformer)
        self.assertEqual(TransformerRegistry.get_transformer({
            'name': 'test.key'
        }), mocked_transformer())

        TransformerRegistry.register('test.key')(mocked_transformer2)
        self.assertEqual(TransformerRegistry.get_transformer({
            'name': 'test.key'
        }), mocked_transformer2())
