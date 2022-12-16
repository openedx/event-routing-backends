"""
Transformers for enrollment related events.
"""

from event_routing_backends.helpers import get_course_from_id
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer


@CaliperTransformersRegistry.register('edx.course.enrollment.activated')
@CaliperTransformersRegistry.register('edx.course.enrollment.deactivated')
@CaliperTransformersRegistry.register('edx.course.grade.passed.first_time')
class EnrollmentEventTransformers(CaliperTransformer):
    """
    This transformer transforms three events:
        - edx.course.enrollment.activated
            Generated when a user is enrolled in a course.

        - edx.course.enrollment.deactivated
            Generated when a user is unenrolled from a course.

        - edx.course.grade.passed.first_time
            Generated when a user complete a course.
    """

    type = 'Event'

    def get_action(self):
        """
        Return action for caliper event.

        Returns:
            str
        """
        if self.get_data('name', True) == 'edx.course.enrollment.activated':
            return 'Activated'
        if self.get_data('name', True) == 'edx.course.grade.passed.first_time':
            return 'Completed'
        return 'Deactivated'

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        self.backend_name = 'caliper'
        course = get_course_from_id(self.get_data('context.course_id'))

        # TODO: replace with anonymous enrollment id?
        course_root_url = self.get_object_iri('course', self.get_data('data.course_id', True))
        caliper_object = {
            'id': course_root_url,
            'type': 'CourseOffering',
            'name': course['display_name'],
            'extensions': {'mode': self.get_data('data.mode')} if self.get_data('data.mode') is not None else None,
        }
        return caliper_object
