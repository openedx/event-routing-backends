"""
Base transformer to transform common event fields.
"""
import uuid
from logging import getLogger

from django.contrib.auth import get_user_model

from event_routing_backends.processors.caliper.constants import CALIPER_EVENT_CONTEXT
from event_routing_backends.processors.caliper.helpers import convert_datetime_to_iso
from event_routing_backends.processors.mixins.base_transformer import BaseTransformerMixin
from student.models import anonymous_id_for_user  # pylint: disable=import-error

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
        self._add_referrer()

    def _add_generic_fields(self):
        """
        Add all of the generic fields to the transformed_event object.
        """
        self.transformed_event.update({
            '@context': CALIPER_EVENT_CONTEXT,
            'id': uuid.uuid4().urn,
            'eventTime': convert_datetime_to_iso(self.event.get('timestamp'))
        })
        self.transformed_event['object'] = {
            'extensions': {
                'course_id': self.event['context'].get('course_id', '')
            }
        }

    def _add_actor_info(self):
        """
        Add all generic information related to `actor`.
        """
        anonymous_id = self._generate_anonymous_id()

        self.transformed_event['actor'] = {
            'id': anonymous_id,
            'type': 'Person'
        }

    def _generate_anonymous_id(self):
        """
        Generate anonymous user id.

        If no anonymous id is generated, return "anonymous"

        Returns:
            str
        """
        username = self.event['context'].get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error('User with username "{}" does not exist. '
                         'Cannot generate anonymous ID'.format(username))

            anonymous_id = 'anonymous'
        else:
            anonymous_id = anonymous_id_for_user(user, None)

        return anonymous_id

    def _add_referrer(self):
        """
        Adds information of an Entity that represents the referring context.
        """
        self.transformed_event['referrer'] = {
            'id': self.event['context'].get('referer'),
            'type': 'WebPage'
        }

    def transform(self):
        """
        Transform the edX event.

        Overriding this method to clean the event after successfull
        transformation.
        In some cases, `object[extensions]` in the transfromed event may have
        some keys that already exist in the `object` field of transfromed event.
        Here we delete such fields.

        Returns:
            dict
        """
        transformed_event = super(CaliperTransformer, self).transform()
        self.clean_event(transformed_event, ('id', 'type'))
        return transformed_event

    def clean_event(self, event, ignored_fields=()):
        """
        Remove duplicated fields from event.

        Remove the fields from the event object's extensions that
        already exist in the object.

        There are some fields that have different meaning in `object` than
        the object extensions. e.g. for some video events, `object[id]` has
        different meaning that `object[extensions][id]` hence we do not want
        to delete the `id` key here. Such keys are passed in `ignored_fields`
        parameter.

        Arguments:
            event (dict) :           transformed event
            ignored_fields (tuple) : fields that should be ignored for cleaning
        """
        event_object = event.get('object', {})
        for key in event_object.keys():
            if (
                key in event_object.get('extensions', {}) and
                key not in ignored_fields
            ):
                del event_object['extensions'][key]
