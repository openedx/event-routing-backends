"""
Transformers for enrollment related events.
"""

from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Verb

from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class BaseExamTransformer(XApiTransformer):
    """
    Base transformer for exam events.
    """

    exam_type_activity = None

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        object_id = self.get_data("event.exam_content_id")

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=self.exam_type_activity,
                name=LanguageMap(**({constants.EN: self.get_data("event.exam_name")})),
                extensions=Extensions(
                    {
                        constants.XAPI_ACTIVITY_TIME_LIMIT: self.get_data(
                            "event.exam_default_time_limit_mins"
                        )
                    }
                ),
            ),
        )

    def get_context_activities(self):
        context_activities = super().get_context_activities()

        context_activities.grouping = [
            Activity(
                id=self.get_data("event.attempt_code"),
                definition=ActivityDefinition(
                    type=constants.XAPI_ACTIVITY_EXAM_ATTEMPT,
                    name=LanguageMap({constants.EN: self.get_data("event.exam_name")}),
                    extensions=Extensions(
                        {
                            constants.XAPI_CONTEXT_ATTEMPT_STARTED: self.get_data(
                                "event.attempt_started_at"
                            ),
                            constants.XAPI_CONTEXT_ATTEMPT_COMPLETED: self.get_data(
                                "event.attempt_completed_at"
                            ),
                            constants.XAPI_CONTEXT_DURATION: self.get_data(
                                "event.attempt_event_elapsed_time_secs"
                            ),
                            constants.XAPI_ACTIVITY_ATTEMPT: self.get_data(
                                "event.attempt_id"
                            ),
                        }
                    ),
                ),
            ),
        ]

        return context_activities


class BaseTimedExamTransformer(BaseExamTransformer):
    """
    Base transformer for timed exam events.
    """

    exam_type_activity = constants.XAPI_ACTIVITY_TIMED_ASSESSMENT


class BasePracticeExamTransformer(BaseExamTransformer):
    """
    Base transformer for practice exam events.
    """

    exam_type_activity = constants.XAPI_ACTIVITY_PRACTICE_ASSESSMENT


class BaseProctoredExamTransformer(BaseExamTransformer):
    """
    Base transformer for proctored exam events.
    """

    exam_type_activity = constants.XAPI_ACTIVITY_PROCTORED_ASSESSMENT


class InitializedMixin:
    """
    Base transformer for initialized exam events
    """

    verb = Verb(
        id=constants.XAPI_VERB_INITIALIZED,
        display=LanguageMap({constants.EN: constants.INITIALIZED}),
    )


class TerminatedMixin:
    """
    Base transformer for terminated exam events
    """

    verb = Verb(
        id=constants.XAPI_VERB_TERMINATED,
        display=LanguageMap({constants.EN: constants.TERMINATED}),
    )


@XApiTransformersRegistry.register("edx.special_exam.timed.attempt.created")
class TimedExamCreatedTransformer(BaseTimedExamTransformer, InitializedMixin):
    """
    Transformers for event generated when learner start an exam attempt.
    """


@XApiTransformersRegistry.register("edx.special_exam.practice.attempt.created")
class PracticeExamCreatedTransformer(BasePracticeExamTransformer, InitializedMixin):
    """
    Transformers for event generated when learner start an exam attempt.
    """


@XApiTransformersRegistry.register("edx.special_exam.proctored.attempt.created")
class ProctoredExamCreatedTransformer(BaseProctoredExamTransformer, InitializedMixin):
    """
    Transformers for event generated when learner start an exam attempt.
    """


@XApiTransformersRegistry.register("edx.special_exam.timed.attempt.submitted")
class TimedExamSubmittedTransformer(BaseTimedExamTransformer, TerminatedMixin):
    """
    Transformers for event generated when learner submit an exam attempt.
    """


@XApiTransformersRegistry.register("edx.special_exam.practice.attempt.submitted")
class PracticeExamSubmittedTransformer(BasePracticeExamTransformer, TerminatedMixin):
    """
    Transformers for event generated when learner submit an exam attempt.
    """


@XApiTransformersRegistry.register("edx.special_exam.proctored.attempt.submitted")
class ProctoredExamSubmittedTransformer(BaseProctoredExamTransformer, TerminatedMixin):
    """
    Transformers for event generated when learner submit an exam attempt.
    """
