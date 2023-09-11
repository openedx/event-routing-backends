"""
xAPI Transformer Class
"""
import hashlib

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

from event_routing_backends.helpers import get_anonymous_user_id, get_course_from_id, get_user_email, get_uuid5
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
        transformed_props["version"] = constants.XAPI_SPECIFICATION_VERSION
        return Statement(**transformed_props)

    def base_transform(self):
        """
        Transform the fields that are common for all events.
        """
        actor = self.get_actor()
        event_timestamp = self.get_timestamp()
        self.transformed_event = {
            'actor': actor,
            'context': self.get_context(),
            'timestamp': event_timestamp,
        }
        # Warning! changing anything in these 2 lines or changing the "base_uuid" can invalidate
        # billions of rows in the database. Please have a community discussion first before introducing
        # any change in generation of UUID.
        uuid_str = f'{actor.to_json()}-{event_timestamp}'
        self.transformed_event['id'] = get_uuid5(self.verb.to_json(), uuid_str)  # pylint: disable=no-member

    def get_actor(self):
        """
        Return `Agent` object for the event.

        Returns:
            `Agent`
        """

        if settings.XAPI_AGENT_IFI_TYPE == 'mbox':
            email = get_user_email(self.extract_username_or_userid())
            agent = Agent(mbox=email)
        elif settings.XAPI_AGENT_IFI_TYPE == 'mbox_sha1sum':
            email = get_user_email(self.extract_username_or_userid())
            mbox_sha1sum = hashlib.sha1(email.encode('utf-8')).hexdigest()
            agent = Agent(mbox_sha1sum=mbox_sha1sum)
        else:
            user_uuid = get_anonymous_user_id(self.extract_username_or_userid(), 'XAPI')
            agent = Agent(
                account={"homePage": settings.LMS_ROOT_URL, "name": user_uuid}
            )
        return agent

    def get_timestamp(self):
        """
        Get the Timestamp for the statement.

        Returns:
            str
        """
        return self.get_data('timestamp') or self.get_data('time')

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
                constants.XAPI_TRANSFORMER_VERSION_KEY: self.transformer_version,
                constants.XAPI_CONTEXT_SESSION_ID: self.extract_sessionid()
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

    @property
    def verb(self):
        """
        Get verb for xAPI transformed event.

        Returns:
            `Verb`
        """
        event_name = self.get_data('name', True)

        event_source = self.get_data('event_source') or self.get_data('context.event_source')
        if event_source == 'browser' and event_name == 'problem_check':
            verb = self.verb_map['problem_check_browser']
        else:
            verb = self.verb_map[event_name]

        return Verb(
            id=verb['id'],
            display=LanguageMap({constants.EN: verb['display']})
        )
