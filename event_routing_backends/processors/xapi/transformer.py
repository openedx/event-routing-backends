"""
xAPI Transformer Class
"""

from tincan import Agent, LanguageMap, Statement, Verb

from event_routing_backends.helpers import get_anonymous_user_id_by_username
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin
from event_routing_backends.processors.xapi import constants


class XApiTransformer(BaseTransformerMixin):
    """
    xAPI Transformer Class
    """
    required_fields = (
        'object',
        'verb',
    )

    def transform(self):
        """
        Return transformed `Statement` object.

        `BaseTransformer`'s `transform` method will return dict containing
        xAPI objects in transformed fields. Here we return a `Statement` object
        constructed using those fields.

        Returns:
            `Statement`
        """
        transformed_props = super().transform()
        transformed_props["version"] = constants.XAPI_TRANSFORMER_VERSION
        return Statement(**transformed_props)

    def base_transform(self):
        """
        Transform the fields that are common for all events.
        """
        # TODO: Move context registration in base transform
        self.transformed_event = {
            'actor': self.get_actor(),
            'timestamp': self.get_timestamp()
        }

    def get_actor(self):
        """
        Return `Agent` object for the event.

        Returns:
            `Agent`
        """

        user_uuid = get_anonymous_user_id_by_username(self.extract_username())
        return Agent(
            openid='https://openedx.org/users/user-v1/%s' % user_uuid,
        )

    def get_timestamp(self):
        """
        Get the Timestamp for the statement.

        Returns:
            str
        """
        return self.get_data('timestamp')


class XApiVerbTransformerMixin:
    """
    Return transformed Verb object using a predefined `verb_map`
    in the transformer.

    The `verb_map` dictionary must contain `id` and `display` (language "en")
    for each verb value.

    This is helpful in base transformer class which are going to be
    transforming multiple transformers.
    """
    verb_map = None

    def get_verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        event_name = self.get_data('name', True)

        verb = self.verb_map[event_name]

        return Verb(
            id=verb['id'],
            display=LanguageMap({constants.EN: verb['display']})
        )
