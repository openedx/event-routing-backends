"""
Transformers for forum related events.
"""
from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Result, Verb

from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


@XApiTransformersRegistry.register("edx.completion.block_completion.changed")
class CompletionCreatedTransformer(XApiTransformer):
    """
    Transformers for event generated when an student completion is created or updated.
    """

    verb = Verb(
        id=constants.XAPI_VERB_PROGRESSED,
        display=LanguageMap({constants.EN: constants.PROGRESSED}),
    )

    additional_fields = ('result', )

    def get_object(self):
        """
        Get object for xAPI transformed event related to a thread.

        Returns:
            `Activity`
        """
        return Activity(
            id=self.get_object_iri("xblock", self.get_data("data.block_id")),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_RESOURCE,
            ),
        )

    def get_result(self):
        """
        Get result for xAPI transformed event related to a thread.

        Returns:
            `Result`
        """
        return Result(
            completion=self.get_data("data.completion") == 1.0,
            extensions=Extensions(
                {constants.XAPI_ACTIVITY_PROGRESS: self.get_data("data.completion")*100}
            ),
        )
