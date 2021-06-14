"""
Transformers for enrollment related events.
"""
import logging

from django.conf import settings
from django.urls import reverse

from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

logger = logging.getLogger('caliper_tracking')


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
        data = self.event['data'].copy()

        # TODO: replace with anonymous enrollment id?
        if 'course_id' in data and data['course_id']:
            course_root_url = '{root_url}{course_root}'.format(
                root_url=settings.LMS_ROOT_URL,
                course_root=reverse('course_root', kwargs={'course_id': data['course_id']})
            )
        else:
            course_root_url = None
            logger.info(
                'Course id not found!',
            )
        caliper_object = {
            **({'id': course_root_url} if course_root_url is not None else {}),
            'type': 'Membership',
            'extensions': self.extract_subdict_by_keys(data, ['course_id', 'mode']),
        }
        return caliper_object
