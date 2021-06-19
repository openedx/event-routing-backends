"""
Base Transformer Mixin to add or transform common data values.
"""
import logging

from event_routing_backends.models import get_value_from_dotted_path

logger = logging.getLogger(__name__)


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

    def extract_subdict_by_keys(self, base_dict, keys):
        """
        Extract a subdict from given dict.
        Subdict would have only those keys provided in `keys` argument.
        If given key is not present in provided dict it will be ignored.
        Arguments:
            base_dict (dict)    :  dictionay to extract keys from
            keys (list)         :  list of keys need in extracted dict
        Returns:
            dict
        """
        # ignore the key if it is not in the original dict
        keys_ignored = set(keys) - set(base_dict.keys())
        if keys_ignored:
            logger.info(
                'Following keys are ignored: %s',
                str(keys_ignored)
            )
        return {key: base_dict[key] for key in set(keys).intersection(base_dict.keys())}

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
                        key, self.__class__.__name__, self.get_data('name', True)
                    )
                )
        self.transformed_event = self.del_none(self.transformed_event)

        return self.transformed_event

    def extract_username(self):
        """
        Extracts username from event by finding it in context first and falling back to data
        if context does have username key

        Returns:
            str
        """
        username = self.get_data('context.username')
        if username is None:
            username = self.get_data('data.username', True)
        return username

    def get_data(self, key, required=False):
        """
        Map the dotted key to nested keys for event dict and return the matching value.If key is required field and
        not fond in event and error will be logged else an info will be logged

        For example:
            'key_a.key_b.key_c' will look for the following value:

            {
                'key_a': {
                    'key_b': {
                        'key_c': 'final value'
                    }
                }
            }

        Arguments:
            key (str)  :    dotted key string for the event dict
            required (bool) :    key is a required field of event or not.

        Returns:
            ANY :                 Returns the value found in the event dict or `None` if
                                  no value exists for provided dotted path.
        """
        result = get_value_from_dotted_path(self.event, key)
        if result is None:
            if not required:
                logger.info('Could not get data for %s in event "%s"', key, self.get_data('name', True))
            else:
                raise ValueError(
                    'Could not get data for {} in event "{}"'.format(key, self.get_data('name', True))
                )

        return result

    def del_none(self, source_dict):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.

        This alters the input so you may wish to ``copy`` the dict first.
        """
        for key, value in list(source_dict.items()):
            if value is None:
                del source_dict[key]
            elif isinstance(value, dict):
                self.del_none(value)
        return source_dict
