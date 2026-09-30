"""
Registry to keep track of Caliper event transformers
"""
from event_routing_backends.processors.transformer_utils.registry import TransformerRegistry


class CaliperTransformersRegistry(TransformerRegistry):
    """
    Registry to keep track of Caliper event transformers
    """
    mapping = {}
