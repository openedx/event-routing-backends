"""
Base transformer to transform common event fields.
"""
import uuid

from django.contrib.auth import get_user_model

from event_routing_backends.helpers import convert_datetime_to_iso, get_anonymous_user_id
from event_routing_backends.processors.caliper.constants import CALIPER_EVENT_CONTEXT
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin

User = get_user_model()


class CaliperTransformer(BaseTransformerMixin):
    """
    Base transformer class to transform common fields.
    """
    required_fields = (
        'type',
        'object',
        'action'
    )

    def base_transform(self):
        """
        Transform common Caliper fields.
        """
        self._add_generic_fields()
        self._add_actor_info()
        self._add_session_info()

    def _add_generic_fields(self):
        """
        Add all of the generic fields to the transformed_event object.
        """
        self.transformed_event.update({
            '@context': CALIPER_EVENT_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime_to_iso(self.get_data('timestamp', True)),
            'extensions': {}
        })
        self.transformed_event['object'] = {}
        course_id = self.get_data('context.course_id')
        if course_id is not None:
            extensions = {"isPartOf": {}}
            extensions['isPartOf']['id'] = self.get_object_iri('course', course_id)
            extensions['isPartOf']['type'] = 'CourseOffering'
            self.transformed_event['object']['extensions'] = {}
            self.transformed_event['object']['extensions'].update(extensions)

    def _add_actor_info(self):
        """
        Add all generic information related to `actor`.
        """
        self.transformed_event['actor'] = {
            'id': self.get_object_iri(
                'user',
                get_anonymous_user_id(self.extract_username_or_userid(), 'CALIPER'),
            ),
            'type': 'Person'
        }

    def _add_session_info(self):
        """
        Add session info related to the event
        """
        sessionid = self.extract_sessionid()
        if sessionid:
            self.transformed_event['session'] = {
                'id': self.get_object_iri(
                    'sessions',
                    sessionid,
                ),
                'type': 'Session'
            }
