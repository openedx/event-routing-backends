"""
Base Transformer Mixin to add or transform common data values.
"""


class BaseTransformerMixin:
    """
    Base Transformer Mixin class.

    Other transformers are inherited from this class.
    """
    required_fields = ()
    additional_fields = ()

    def __init__(self, event):
        """
        Initialize the transformer with the event to be transformed.

        Arguments:
            event (dict)    :   event to be transformed
        """
        self.event = event.copy()
        self.transformed_event = {}

    def find_nested(self, key):
        """
        Find a key at all levels in the original event dictionary.

        Arguments:
            key (str)         :  dictionary key

        Returns:
            ANY
        """
        def _find_nested(event_dict):
            """
            Inner recursive method to find the key in dict.

            Arguments:
                event_dict (dict) :  event dictionary object

            Returns:
                ANY
            """
            if key in event_dict:
                return event_dict[key]
            for _, value in event_dict.items():
                if isinstance(value, dict):
                    found = _find_nested(value)
                    if found is not None:
                        return found
            return None

        return _find_nested(self.event)

    def base_transform(self):
        """
        Transform the fields that are common for all events.

        Other classes can override this method to add common transformation
        code for events.
        """
        return

    def transform(self):
        """
        Transform the edX event.

        Returns:
            dict
        """
        self.base_transform()

        transforming_fields = self.required_fields + self.additional_fields
        for key in transforming_fields:
            if hasattr(self, key):
                value = getattr(self, key)
                self.transformed_event[key] = value
            elif hasattr(self, f'get_{key}'):
                value = getattr(self, f'get_{key}')()
                self.transformed_event[key] = value
            else:
                raise ValueError(
                    'Cannot find value for "{}" in transformer {} for the event "{}"'.format(
                        key, self.__class__.__name__, self.event['name']
                    )
                )

        return self.transformed_event
