"""
Transformers for progress related events.
"""
from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Result, Verb

from event_routing_backends.processors.openedx_filters.decorators import openedx_filter
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class BaseProgressTransformer(XApiTransformer):
    """
    Base transformer for progress events.
    """
    _verb = Verb(
        id=constants.XAPI_VERB_PROGRESSED,
        display=LanguageMap({constants.EN: constants.PROGRESSED}),
    )
    object_type = None
    additional_fields = ('result', )

    @openedx_filter(
        filter_type="event_routing_backends.processors.xapi.progress_events.base_progress.get_object",
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

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        return Result(
            completion=self.get_data("data.percent") == 1.0,
            score={
                "scaled": self.get_data("data.percent") or 0
            }
        )


@XApiTransformersRegistry.register("edx.completion.block_completion.changed")
class CompletionCreatedTransformer(BaseProgressTransformer):
    """
    Transformers for event generated when BlockCompletion record is created or updated.
    """
    object_type = constants.XAPI_ACTIVITY_RESOURCE

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        return Result(
            completion=self.get_data("data.completion") == 1.0,
            extensions=Extensions(
                {constants.XAPI_ACTIVITY_PROGRESS: self.get_data("data.completion") * 100}
            ),
        )


@XApiTransformersRegistry.register("edx.completion_aggregator.progress.chapter")
@XApiTransformersRegistry.register("edx.completion_aggregator.progress.sequential")
@XApiTransformersRegistry.register("edx.completion_aggregator.progress.vertical")
class ModuleProgressTransformer(BaseProgressTransformer):
    """
    Transformer for event generated when a user makes progress in a section, subsection or unit.
    """
    object_type = constants.XAPI_ACTIVITY_MODULE


@XApiTransformersRegistry.register("edx.completion_aggregator.progress.course")
class CourseProgressTransformer(BaseProgressTransformer):
    """
    Transformer for event generated when a user makes progress in a course.
    """
    object_type = constants.XAPI_ACTIVITY_COURSE
