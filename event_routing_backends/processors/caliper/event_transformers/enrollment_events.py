"""
Transformers for enrollment related events.
"""

from event_routing_backends.helpers import make_course_url
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer


@CaliperTransformersRegistry.register('edx.course.enrollment.activated')
@CaliperTransformersRegistry.register('edx.course.enrollment.deactivated')
class EnrollmentEventTransformers(CaliperTransformer):
    """
    This transformer transformes two events:
        - edx.course.enrollment.activated
            Generated when a user is enrolled in a course.

        - edx.course.enrollment.deactivated
            Generated when a user is unenrolled from a course.
    """

    type = 'Event'

    def get_action(self):
        """
        Return action for caliper event.

        Returns:
            str
        """
        if self.event['name'] == 'edx.course.enrollment.activated':
            return 'Activated'
        return 'Deactivated'

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        data = self.get_data('data')

        # TODO: replace with anonymous enrollment id?
        course_root_url = make_course_url(self.get_data('data.course_id', True))
        caliper_object = {
            'id': course_root_url,
            'type': 'Membership',
            'extensions': self.extract_subdict_by_keys(data, ['course_id', 'mode']),
        }
        return caliper_object
