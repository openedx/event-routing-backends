"""
Registry to keep track of event transformers
"""
from logging import getLogger

from event_routing_backends.processors.transformer_utils.exceptions import NoTransformerImplemented

logger = getLogger(__name__)


class TransformerRegistry:
    """
    Registry to keep track of event transformers.

    Every Registry that inherits this registry MUST has its own `mapping`
    class attribute to avoid conflicts.
    """
    mapping = {}

    @classmethod
    def validate_mapping_exists(cls):
        """
        Validate that every registry inheriting this one has its own `mapping` attribute.

        Raises:
            AttributeError
        """
        if 'mapping' not in cls.__dict__:
            raise AttributeError(
                '{} registry must has its own "mapping" class attribute.'.format(
                    cls.__name__
                )
            )

    @classmethod
    def register(cls, event_key):
        """
        Decorator to register a transformer for an event.

        Arguments:
            event_key (str):    unique event identifier string.
        """
        cls.validate_mapping_exists()

        def __inner__(transformer):
            """
            Register transformer for a given event.

            Arguments:
                transformer (class):    transformer class for one or more events.
            """
            if event_key in cls.mapping:
                logger.info(
                    'Overriding the existing transformer {old_transformer} for event '
                    '{event_name} with {new_transformer}'.format(
                        old_transformer=cls.mapping[event_key],
                        new_transformer=transformer,
                        event_name=event_key
                    )
                )
                cls.mapping[event_key] = transformer

            else:
                logger.debug(
                    'Registered transformer {transformer} for event {event_name} '.format(
                        transformer=transformer,
                        event_name=event_key
                    )
                )
                cls.mapping[event_key] = transformer
            return transformer

        return __inner__

    @classmethod
    def get_transformer(cls, event):
        """
        Return an initialized transformer instance for the provided `event`.

        Arguments:
            event (dict):   event to be transformed

        Returns:
            Transformer object

        Raises:
            `NoTransformerImplemented`:  if matching transformer is not found.
        """
        event_name = event.get('name')
        try:
            return cls.mapping[event_name](event)
        except KeyError as error:
            raise NoTransformerImplemented from error
