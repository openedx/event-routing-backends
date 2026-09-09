"""
Registry to keep track of xAPI event transformers
"""
from event_routing_backends.processors.transformer_utils.registry import TransformerRegistry


class XApiTransformersRegistry(TransformerRegistry):
    """
    Registry to keep track of xAPI event transformers
    """
    mapping = {}
