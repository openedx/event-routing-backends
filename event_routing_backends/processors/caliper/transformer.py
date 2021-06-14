"""
Base transformer to transform common event fields.
"""
import uuid
from logging import getLogger

from django.contrib.auth import get_user_model

from event_routing_backends.helpers import convert_datetime_to_iso, get_anonymous_user_id_by_username
from event_routing_backends.processors.caliper.constants import CALIPER_EVENT_CONTEXT
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin

logger = getLogger()
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
            **({'eventTime': convert_datetime_to_iso(self.event.get('timestamp'))}
               if self.event.get('timestamp') is not None else {})
        })
        if self.event['context'].get('course_id', ''):
            self.transformed_event['object'] = {
                'extensions': {
                    'course_id': self.event['context'].get('course_id', '')
                }
            }
        else:
            logger.info(
                'In Event %s no course_id found!',
                self.event
            )

    def _add_actor_info(self):
        """
        Add all generic information related to `actor`.
        """
        self.transformed_event['actor'] = {
            'id': get_anonymous_user_id_by_username(self.extract_username()),
            'type': 'Person'
        }

        if not self.extract_username():
            logger.info(
                'In Event %s username not found!',
                self.event
            )
