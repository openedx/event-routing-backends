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
    StatementRef,
    Verb,
)

from event_routing_backends.helpers import get_anonymous_user_id, get_course_from_id, get_user_email, get_uuid5
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin
from event_routing_backends.processors.openedx_filters.decorators import openedx_filter
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

    def base_transform(self, transformed_event):
        """
        Transform the fields that are common for all events.
        """
        transformed_event = super().base_transform(transformed_event)
        transformed_event.update({
            'id': self.get_event_id(),
            'actor': self.get_actor(),
            'context': self.get_context(),
            'timestamp': self.get_timestamp(),
        })
        return transformed_event

    def get_event_id(self):
        """
        Generates the UUID for this event.

        Uses the actor, event timestamp, and verb to generate a UUID for this event
        which will be the same even if this event is re-processed.

        Returns:
            UUID
        """
        # Warning! changing anything in these 2 lines or changing the "base_uuid" can invalidate
        # billions of rows in the database. Please have a community discussion first before introducing
        # any change in generation of UUID.
        actor = self.get_actor()
        event_timestamp = self.get_timestamp()
        uuid_str = f'{actor.to_json()}-{event_timestamp}'
        return get_uuid5(self.get_verb().to_json(), uuid_str)

    @openedx_filter(filter_type="event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor")
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

    @openedx_filter(filter_type="event_routing_backends.processors.xapi.transformer.xapi_transformer.get_verb")
    def get_verb(self):
        """
        This intercepts the super verb value or the attribute class `_verb` in order to allow the openedx
        filters implementation.
        """
        return super().get_verb() if hasattr(super(), "get_verb") else self._verb  # pylint: disable=no-member

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

    def get_verb(self):
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


class OneToManyXApiTransformerMixin:
    """
    Abstract mixin that helps transform a single input event into:

    * 1 parent xAPI event, plus
    * N "child" xAPI events, where N>=0
    """
    @property
    def child_transformer_class(self):
        """
        Abstract property which returns the transformer class to use when transforming the child events.

        Should inherit from OneToManyChildXApiTransformerMixin.

        Returns:
            Type
        """
        raise NotImplementedError

    def get_child_ids(self):
        """
        Abstract method which returns the list of "child" event IDs from the parent event data.

        Returns:
            list of strings
        """
        raise NotImplementedError

    def transform(self):
        """
        Transform the edX event into a list of events, if there is child data.

        If transform_child_events() is Falsey, then only the parent event is returned.
        Otherwise, returns a list containing the parent event, followed by any child events.

        Returns:
            ANY, or list of ANY
        """
        parent_event = super().transform()
        child_events = self.transform_children(parent_event)
        if child_events:
            return [parent_event, *child_events]
        return parent_event

    def transform_children(self, parent):
        """
        Transform the children of the parent xAPI event.


        Returns:
            list of ANY
        """
        child_ids = self.get_child_ids()
        ChildTransformer = self.child_transformer_class
        return [
            ChildTransformer(
                child_id=child_id,
                parent=parent,
                event=self.event,
            ).transform() for child_id in child_ids
        ]


class OneToManyChildXApiTransformerMixin:
    """
    Mixin for processing child xAPI events from a parent transformer.

    This class handles initialization, and adds methods for the expected stanzas in the transformed child event.

    The parent event transformer should inherit from OneToManyXApiTransformer.
    """

    def __init__(self, parent, child_id, *args, **kwargs):
        """
        Stores the parent event transformer, and this child's identifier,
        for use when transforming the child data.
        """
        super().__init__(*args, **kwargs)
        self.parent = parent
        self.child_id = child_id

    def get_event_id(self):
        """
        Generates the UUID for this event.

        Uses the actor, event timestamp, verb, and child_id to generate a UUID for this child event
        which ensures a unique event ID for each child event which also differs from the parent event,
        which will be the same even if this event is re-processed.

        Returns:
            UUID
        """
        # Warning! changing anything in these 2 lines or changing the "base_uuid" can invalidate
        # billions of rows in the database. Please have a community discussion first before introducing
        # any change in generation of UUID.
        actor = self.get_actor()
        event_timestamp = self.get_timestamp()
        name = f'{actor.to_json()}-{event_timestamp}'
        namespace_key = f'{self.get_verb().to_json()}-{self.child_id}'
        return get_uuid5(namespace_key, name)

    def get_context(self):
        """
        Returns the context for the xAPI transformed child event.

        Returns:
            `Context`
        """
        return Context(
            extensions=self.get_context_extensions(),
            contextActivities=self.get_context_activities(),
            statement=self.get_context_statement(),
        )

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        return ContextActivities(
            parent=ActivityList([self.parent.object]),
            grouping=ActivityList(self.parent.context.context_activities.parent),
        )

    def get_context_statement(self):
        """
        Returns a StatementRef that refers to the parent event.
        Returns:
            `StatementRef`
        """
        return StatementRef(
            id=self.parent.id,
        )
