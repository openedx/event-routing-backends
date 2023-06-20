"""
Base Transformer Mixin to add or transform common data values.
"""
import logging

from django.conf import settings

from event_routing_backends import __version__
from event_routing_backends.models import get_value_from_dotted_path

logger = logging.getLogger(__name__)


class BaseTransformerMixin:
    """
    Base Transformer Mixin class.

    Other transformers are inherited from this class.
    """

    required_fields = ()
    additional_fields = ()
    backend_name = None

    def __init__(self, event):
        """
        Initialize the transformer with the event to be transformed.

        Arguments:
            event (dict)    :   event to be transformed
        """
        self.event = event.copy()
        self.transformed_event = {}

    @staticmethod
    def find_nested(source_dict, key):
        """
        Find a key at all levels in the original event dictionary.

        Arguments:
            source_dict (dict) :  event dictionary object
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

        return _find_nested(source_dict)

    def base_transform(self):
        """
        Transform the fields that are common for all events.

        Other classes can override this method to add common transformation
        code for events.
        """
        return

    @property
    def transformer_version(self):
        """
        Version of transformer.

        version of transformer package used to transform events
        """

        if getattr(settings, 'RUNNING_WITH_TEST_SETTINGS', False):
            return "{}@{}".format("event-routing-backends", "1.1.1")
        else:
            return "{}@{}".format("event-routing-backends", __version__)

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
                    'Cannot find value for "{}" in transformer {} for the edx event "{}"'.format(
                        key, self.__class__.__name__, self.get_data('name', True)
                    )
                )

        if self.backend_name == 'caliper':
            self.transformed_event['extensions']['transformerVersion'] = self.transformer_version

        self.transformed_event = self.del_none(self.transformed_event)

        return self.transformed_event

    def extract_username_or_userid(self):
        """
        Extracts username or user_id from event by finding it in context first and falling back to data
        if context does have username key

        Returns:
            str
        """
        username_or_id = self.get_data('username') or self.get_data('user_id')
        if not username_or_id:
            username_or_id = self.get_data('data.username') or self.get_data('data.user_id')
            if not username_or_id:
                username_or_id = self.get_data('context.username') or self.get_data('context.user_id')
        return username_or_id

    def extract_sessionid(self):
        """
        Extracts sessionid of user from event either under context or data dictionaries

        Returns:
            str
        """
        return self.get_data('session') or self.get_data('context.session') or self.get_data('data.session')

    def get_data(self, key, required=False):
        """
        This function returns value in self.event against a specified key.

        Hierarchy levels in a nested key are separated by '.' (dot). If required is True and key is not found or is
        empty, the function will raise an exception. If required is False and key is not found or is empty, the
        function will log the instance.

        Parameters:
                key (str): dotted-separated key string
                required (bool) : whether or not key is a required field (default: False)
        Returns:
                ANY (str) : value of key in self.event or 'None' if key is not found or is empty
        Raises:
                ValueError : If key is not found or is empty and required is True
        Example:
                key = 'key_a.key_b.key_c' will return 'value_abc' if:
                self.event = {
                    'key_a': {
                        'key_b': {
                            'key_c': 'value_abc'
                        }
                    }
                }
        """
        if '.' in key:
            result = get_value_from_dotted_path(self.event, key)
        else:
            result = BaseTransformerMixin.find_nested(self.event, key)

        if result != 0 and not result:
            result = None

        if result is None:
            if not required:
                logger.warning('Could not get value for %s in event "%s"', key, self.event.get('name', None))
            else:
                raise ValueError(
                    'Could not get value for {} in event "{}"'.format(key, self.event.get('name', None))
                )

        return result

    def del_none(self, source_dict):
        """
        Delete keys with the value ``None`` in a dictionary, recursively.

        This alters the input so you may wish to ``copy`` the dict first.
        """
        for key, value in list(source_dict.items()):
            if value is None or (value != 0 and not value):
                del source_dict[key]
            elif isinstance(value, dict):
                self.del_none(value)

        return source_dict

    def get_object_iri(self, object_type, object_id):
        """
        Inner recursive method to find the key in dict.

        Arguments:
            object_type (str) :  object type string like course/block
            object_id (str) :  object id string

        Returns:
            str
        """
        if object_id is None or object_type is None:
            return None

        return '{root_url}/{object_type}/{object_id}'.format(
            root_url=settings.LMS_ROOT_URL,
            object_type=object_type,
            object_id=object_id
        )
