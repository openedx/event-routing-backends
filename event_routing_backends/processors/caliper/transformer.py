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
        'action',
        'extensions',
    )

    def base_transform(self, transformed_event):
        """
        Transform common Caliper fields.
        """
        transformed_event = super().base_transform(transformed_event)
        self._add_generic_fields(transformed_event)
        self._add_actor_info(transformed_event)
        self._add_session_info(transformed_event)
        return transformed_event

    def _add_generic_fields(self, transformed_event):
        """
        Add all of the generic fields to the transformed_event object.
        """
        transformed_event.update({
            '@context': CALIPER_EVENT_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime_to_iso(self.get_data('timestamp', True)),
        })

    def _add_actor_info(self, transformed_event):
        """
        Add all generic information related to `actor` to the transformed_event.
        """
        transformed_event['actor'] = {
            'id': self.get_object_iri(
                'user',
                get_anonymous_user_id(self.extract_username_or_userid(), 'CALIPER'),
            ),
            'type': 'Person'
        }

    def _add_session_info(self, transformed_event):
        """
        Add session info related to the transformed_event.
        """
        sessionid = self.extract_sessionid()
        if sessionid:
            transformed_event['session'] = {
                'id': self.get_object_iri(
                    'sessions',
                    sessionid,
                ),
                'type': 'Session'
            }

    def get_object(self):
        """
        Return object for the event.

        Returns:
            dict
        """
        caliper_object = super().get_object()
        course_id = self.get_data('context.course_id')
        if course_id is not None:
            extensions = {"isPartOf": {}}
            extensions['isPartOf']['id'] = self.get_object_iri('course', course_id)
            extensions['isPartOf']['type'] = 'CourseOffering'
            caliper_object['extensions'] = {}
            caliper_object['extensions'].update(extensions)

        return caliper_object

    def get_extensions(self):
        """
        Return extensions for the event.

        Returns:
            dict
        """
        return {
            'transformerVersion': self.transformer_version,
        }
