"""
Transformers for navigation related events.
"""
from tincan import Activity, ActivityDefinition, ActivityList, Context, ContextActivities, Extensions, LanguageMap

from event_routing_backends.helpers import get_anonymous_user_id_by_username, make_course_url
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer, XApiVerbTransformerMixin

VERB_MAP = {
    'edx.ui.lms.sequence.next_selected': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },
    'edx.ui.lms.sequence.previous_selected': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },
    'edx.ui.lms.sequence.tab_selected': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    },
    'edx.ui.lms.link_clicked': {
        'id': constants.XAPI_VERB_EXPERIENCED,
        'display': constants.EXPERIENCED
    },
    'edx.ui.lms.sequence.outline.selected': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    },
    'edx.ui.lms.outline.selected': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    }
}


class NavigationTransformersMixin(XApiTransformer, XApiVerbTransformerMixin):
    """
    Base transformer class for navigation events.

    This class has the common attributes for all navigation events.
    """
    additional_fields = ('context', )
    verb_map = VERB_MAP
    event_version = 1.0


@XApiTransformersRegistry.register('edx.ui.lms.link_clicked')
class LinkClickedTransformer(NavigationTransformersMixin):
    """
    xAPI transformer for event generated when user clicks a link.
    """

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        return Activity(
            id=self.get_data('data.target_url', True),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_LINK,
                name=LanguageMap({constants.EN: 'Link name'}),
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_POSITION: self.get_data('data.target_url')
                })
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """

        context = Context(
            registration=get_anonymous_user_id_by_username(
                self.extract_username()
            ),
            contextActivities=self.get_context_activities()
        )
        context.extensions = Extensions({"eventVersion": self.event_version})
        return context

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id=make_course_url(self.get_data('context.course_id')),
                object_type=constants.XAPI_ACTIVITY_COURSE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )


@ XApiTransformersRegistry.register('edx.ui.lms.sequence.outline.selected')
@ XApiTransformersRegistry.register('edx.ui.lms.outline.selected')
class OutlineSelectedTransformer(NavigationTransformersMixin):
    """
    xAPI transformer for Navigation events.
    """
    additional_fields = ('context', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        return Activity(
            id=self.get_data('data.target_url'),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                name=LanguageMap({constants.EN: self.get_data('data.target_name')}),
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        context = Context(
            registration=get_anonymous_user_id_by_username(
                self.extract_username()
            )
        )
        context.extensions = Extensions({"eventVersion": self.event_version})
        return context


@ XApiTransformersRegistry.register('edx.ui.lms.sequence.next_selected')
@ XApiTransformersRegistry.register('edx.ui.lms.sequence.previous_selected')
@ XApiTransformersRegistry.register('edx.ui.lms.sequence.tab_selected')
class TabNavigationTransformer(NavigationTransformersMixin):
    """
    xAPI transformer for Navigation events.
    """
    additional_fields = ('context', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        if self.get_data('name', True) == 'edx.ui.lms.sequence.tab_selected':
            position = self.get_data('data.target_tab')
        else:
            position = self.get_data('data.current_tab')

        return Activity(
            id=self.get_data('data.id'),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_MODULE,
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_POSITION: position
                })
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        event_name = self.get_data('name', True)
        if event_name == 'edx.ui.lms.sequence.tab_selected':
            extensions = Extensions({
                constants.XAPI_CONTEXT_STARTING_POSITION: self.get_data('data.current_tab'),
                "eventVersion": self.event_version
            })
        elif event_name == 'edx.ui.lms.sequence.next_selected':
            extensions = Extensions({
                constants.XAPI_CONTEXT_ENDING_POSITION: 'next unit',
                "eventVersion": self.event_version
            })
        else:
            extensions = Extensions({
                constants.XAPI_CONTEXT_ENDING_POSITION: 'previous unit',
                "eventVersion": self.event_version
            })

        context = Context(
            registration=get_anonymous_user_id_by_username(
                self.extract_username()
            ),
            contextActivities=self.get_context_activities()
        )
        context.extensions = extensions
        return context

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id=self.get_data('data.id'),
                object_type=constants.XAPI_ACTIVITY_MODULE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )
