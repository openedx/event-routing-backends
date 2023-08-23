"""
Transformers for grading related events.
"""
from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Result, Verb

from event_routing_backends.helpers import get_course_from_id
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


@XApiTransformersRegistry.register("edx.grades.subsection.grade_calculated")
class SubsectionGradedTransformer(XApiTransformer):
    """
    Transformer for event generated when an subsection is graded.
    """

    verb = Verb(
        id=constants.XAPI_VERB_EARNED,
        display=LanguageMap({constants.EN: constants.EARNED}),
    )

    additional_fields = ("result",)

    def get_object(self):
        """
        Get object for xAPI transformed event related to subsection grading.

        Returns:
            `Activity`
        """

        return Activity(
            id=self.get_object_iri("xblock", self.get_data("data.block_id", True)),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_RESOURCE,
            ),
        )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_data = self.get_data("data")
        weighted_possible = event_data["weighted_total_possible"] or 0
        weighted_earned = event_data["weighted_total_earned"] or 0

        if weighted_possible > 0:
            scaled = weighted_earned / weighted_possible
        else:
            scaled = 0
        return Result(
            success=weighted_earned >= weighted_possible,
            score={
                "min": 0,
                "max": weighted_possible,
                "raw": weighted_earned,
                "scaled": scaled,
            },
        )


@XApiTransformersRegistry.register("edx.grades.course.grade_calculated")
class CourseGradedTransformer(XApiTransformer):
    """
    Transformer for event generated when an course is graded.
    """

    verb = Verb(
        id=constants.XAPI_VERB_EARNED,
        display=LanguageMap({constants.EN: constants.EARNED}),
    )

    additional_fields = ("result",)

    def get_object(self):
        """
        Get object for xAPI transformed event related to course grading.

        Returns:
            `Activity`
        """
        course_id = self.get_data("context.course_id", True)
        object_id = self.get_object_iri("course", course_id)
        course = get_course_from_id(course_id)
        display_name = course["display_name"]

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap(
                    **({constants.EN: display_name} if display_name is not None else {})
                ),
            ),
        )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_data = self.get_data("data")
        weighted_possible = 1.0
        weighted_earned = event_data["percent_grade"] or 0

        letter_grade = self.get_data("data.letter_grade") or "Fail"

        return Result(
            score={
                "min": 0,
                "max": weighted_possible,
                "raw": weighted_earned,
                "scaled": weighted_earned,
            },
            extensions=Extensions(
                {
                    constants.XAPI_ACTIVITY_GRADE_CLASSIFICATION: letter_grade
                }
            ),
        )
