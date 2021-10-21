"""
Transformers for navigation related events.
"""
from tincan import Activity, ActivityDefinition, Context, Extensions, LanguageMap

from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer, XApiVerbTransformerMixin

VERB_MAP = {
    'edx.ui.lms.sequence.next_selected': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
    },
    'edx.ui.lms.sequence.previous_selected': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
    },
    'edx.ui.lms.sequence.tab_selected': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
    },
    'edx.ui.lms.link_clicked': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
    },
    'edx.ui.lms.sequence.outline.selected': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
    },
    'edx.ui.lms.outline.selected': {
        'id': constants.XAPI_VERB_NAVIGATED,
        'display': constants.NAVIGATED
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
            id=self.get_data('data.target_url'),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_LINK
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """

        context = Context(
            contextActivities=self.get_context_activities()
        )
        return context


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
                name=LanguageMap({constants.EN: self.get_data('data.target_name')})
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        context = Context(
            contextActivities=self.get_context_activities()
        )
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
        return Activity(
            id=self.get_object_iri('xblock', self.get_data('data.id')),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_RESOURCE,
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_TOTAL_COUNT: self.get_data('data.tab_count')
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
                constants.XAPI_CONTEXT_ENDING_POSITION: self.get_data('data.target_tab'),
            })
        elif event_name == 'edx.ui.lms.sequence.next_selected':
            extensions = Extensions({
                constants.XAPI_CONTEXT_STARTING_POSITION: self.get_data('data.current_tab'),
                constants.XAPI_CONTEXT_ENDING_POSITION: 'next unit',
            })
        else:
            extensions = Extensions({
                constants.XAPI_CONTEXT_STARTING_POSITION: self.get_data('data.current_tab'),
                constants.XAPI_CONTEXT_ENDING_POSITION: 'previous unit',
            })

        context = Context(
            contextActivities=self.get_context_activities()
        )
        context.extensions = extensions
        return context
