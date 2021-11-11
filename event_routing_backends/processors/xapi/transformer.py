"""
xAPI Transformer Class
"""
import uuid

from django.conf import settings
from tincan import (
    Activity,
    ActivityDefinition,
    ActivityList,
    Agent,
    Context,
    ContextActivities,
    Extensions,
    LanguageMap,
    Statement,
    Verb,
)

from event_routing_backends.helpers import get_anonymous_user_id, get_course_from_id
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
        self.transformed_event = {
            'actor': self.get_actor(),
            'context': self.get_context(),
            'timestamp': self.get_timestamp(),
            'id': uuid.uuid4()
        }

    def get_actor(self):
        """
        Return `Agent` object for the event.

        Returns:
            `Agent`
        """

        user_uuid = get_anonymous_user_id(self.extract_username_or_userid())
        return Agent(
            account={"homePage": settings.LMS_ROOT_URL, "name": user_uuid}
        )

    def get_timestamp(self):
        """
        Get the Timestamp for the statement.

        Returns:
            str
        """
        return self.get_data('timestamp')

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        if self.get_data('context.course_id') is not None:
            course = get_course_from_id(self.get_data('context.course_id'))
            course_name = LanguageMap({constants.EN_US: course["display_name"]})
            parent_activities = [
                Activity(
                    id=self.get_object_iri('course', self.get_data('context.course_id')),
                    object_type=constants.XAPI_ACTIVITY_COURSE,
                    definition=ActivityDefinition(
                        type=constants.XAPI_ACTIVITY_COURSE,
                        name=course_name
                    )
                ),
            ]
            return ContextActivities(
                parent=ActivityList(parent_activities),
            )
        else:
            return None

    def get_context(self):
        """
        Get context for xAPI transformed event.
        Returns:
            `Context`
        """
        context = Context(
            extensions=self.get_context_extensions(),
            contextActivities=self.get_context_activities()
        )
        return context

    def get_context_extensions(self):
        return Extensions({
                constants.XAPI_EVENT_VERSION_KEY: self.event_version
            })


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

        if self.get_data('context.event_source') == 'browser' and event_name == 'problem_check':
            verb = self.verb_map['problem_check_browser']
        else:
            verb = self.verb_map[event_name]

        return Verb(
            id=verb['id'],
            display=LanguageMap({constants.EN: verb['display']})
        )
