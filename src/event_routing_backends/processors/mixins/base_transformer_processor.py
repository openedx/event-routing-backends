"""
Base Processor Mixin for transformer processors.
"""
from logging import getLogger

from eventtracking.processors.exceptions import NoBackendEnabled, NoTransformerImplemented

logger = getLogger(__name__)


class BaseTransformerProcessorMixin:
    """
    Base Processor Mixin for transformer processors.

    This mixin is used to transform events into any standard format
    and then route those events to configured endpoints.
    """

    registry = None

    def __call__(self, events):
        """
        Transform the given events, and return the transformed events.

        Arguments:
            event (list of dicts):   Events to be transformed.

        Returns:
            transformed events (list of ANY)

        Raises:
            EventEmissionExit except.on:  if no transformer is registered for an event.
            ANY exception: if raised.
        """
        returned_events = []
        for event in events:
            try:
                transformed_event = self.transform_event(event)
                if not transformed_event:
                    pass
                elif isinstance(transformed_event, list):
                    returned_events += transformed_event
                else:
                    returned_events.append(transformed_event)

            # If the backend isn't enabled at all, early out
            except NoBackendEnabled:
                break
        return returned_events

    def transform_event(self, event):
        """
        Transform the event.

        Transformer method can return transformed events in any data structure format
        (dict, list, or any custom class) but the configured router(s) MUST support it.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            ANY:           transformed event
        """
        event_name = event.get('name')

        try:
            transformed_event = self.get_transformed_event(event)
        except NoTransformerImplemented:
            logger.error('Could not get transformer for %s event.', event_name)
            return None

        except Exception as ex:
            logger.exception(
                'There was an error while trying to transform event "{event}" using'
                ' {processor} processor. Error: {error}'.format(
                    event=event_name,
                    processor=self.__class__.__name__,
                    error=ex
                )
            )
            raise

        return transformed_event

    def get_transformed_event(self, event):
        """
        Transform the event using the class's registry.

        Making this a separate method so that subclasses can override
        this method if those class want to do it some other way.

        Arguments:
            event (dict):   Event to be transformed.

        Returns:
            ANY:           transformed event

        Raises:
            NoTransformerImplemented
        """
        if not self.registry:
            logger.exception('Cannot transform event "{event}". Transformer class '
                             '"{transformer}" must have its own "registry" set.'.format(
                                    event=event['name'],
                                    transformer=self.__class__.__name__
                                ))
            return None
        return self.registry.get_transformer(event).transform()
