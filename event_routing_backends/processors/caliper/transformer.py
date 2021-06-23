"""
Base transformer to transform common event fields.
"""
import uuid

from django.contrib.auth import get_user_model

from event_routing_backends.helpers import convert_datetime_to_iso, get_anonymous_user_id_by_username
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
        self.transformed_event['object'] = {
            'extensions': {
                'course_id': self.get_data('context.course_id')
            }
        }

    def _add_actor_info(self):
        """
        Add all generic information related to `actor`.
        """
        self.transformed_event['actor'] = {
            'id': get_anonymous_user_id_by_username(self.extract_username()),
            'type': 'Person'
        }
