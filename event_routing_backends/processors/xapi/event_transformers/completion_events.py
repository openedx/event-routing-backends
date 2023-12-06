"""
Transformers for completion related events.
"""
from tincan import Activity, ActivityDefinition, LanguageMap, Verb

from event_routing_backends.processors.openedx_filters.decorators import openedx_filter
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class BaseCompletionTransformer(XApiTransformer):
    """
    Base transformer for completion events.
    """
    _verb = Verb(
        id=constants.XAPI_VERB_COMPLETED,
        display=LanguageMap({constants.EN: constants.COMPLETED}),
    )
    object_type = None

    @openedx_filter(
        filter_type="event_routing_backends.processors.xapi.completion_events.base_completion.get_object",
    )
    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        if not self.object_type:
            raise NotImplementedError()

        return Activity(
            id=self.get_object_iri("xblock", self.get_data("data.block_id")),
            definition=ActivityDefinition(
                type=self.object_type,
            ),
        )


@XApiTransformersRegistry.register("edx.completion_aggregator.completion.chapter")
@XApiTransformersRegistry.register("edx.completion_aggregator.completion.sequential")
@XApiTransformersRegistry.register("edx.completion_aggregator.completion.vertical")
class ModuleCompletionTransformer(BaseCompletionTransformer):
    """
    Transformer for events generated when a user completes a section, subsection or unit.
    """
    object_type = constants.XAPI_ACTIVITY_MODULE


@XApiTransformersRegistry.register("edx.completion_aggregator.completion.course")
class CourseCompletionTransformer(BaseCompletionTransformer):
    """
    Transformer for event generated when a user completes a course.
    """
    object_type = constants.XAPI_ACTIVITY_COURSE
