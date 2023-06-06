"""
Transformers for enrollment related events.
"""

from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Verb

from event_routing_backends.helpers import get_course_from_id
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class BaseEnrollmentTransformer(XApiTransformer):
    """
    Base transformer for enrollment events.
    """

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """

        return None

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course_id = self.get_data('context.course_id', True)
        object_id = self.get_object_iri('course', course_id)
        course = get_course_from_id(course_id)
        display_name = course['display_name']

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_COURSE,
                name=LanguageMap(**({constants.EN: display_name} if display_name is not None else {})),
                extensions=Extensions({
                    constants.XAPI_ACTIVITY_MODE: self.get_data('data.mode')
                })
            ),
        )


@XApiTransformersRegistry.register('edx.course.enrollment.activated')
@XApiTransformersRegistry.register('edx.course.enrollment.mode_changed')
class EnrollmentActivatedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner enrolls or gets the enrollment mode changed in a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_REGISTERED,
        display=LanguageMap({constants.EN: constants.REGISTERED}),
    )


@XApiTransformersRegistry.register('edx.course.enrollment.deactivated')
class EnrollmentDeactivatedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner un-enrolls from a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_UNREGISTERED,
        display=LanguageMap({constants.EN: constants.UNREGISTERED}),
    )


@XApiTransformersRegistry.register('edx.course.grade.passed.first_time')
class CourseGradePassedFirstTimeTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner pass course grade first time from a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_PASSED,
        display=LanguageMap({constants.EN: constants.PASSED}),
    )


@XApiTransformersRegistry.register('edx.course.grade.now_passed')
class CourseGradeNowPassedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner pass course grade first time from a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_PASSED,
        display=LanguageMap({constants.EN: constants.PASSED}),
    )


@XApiTransformersRegistry.register('edx.course.grade.now_failed')
class CourseGradeNowFailedTransformer(BaseEnrollmentTransformer):
    """
    Transformers for event generated when learner pass course grade first time from a course.
    """
    verb = Verb(
        id=constants.XAPI_VERB_FAILED,
        display=LanguageMap({constants.EN: constants.FAILED}),
    )
