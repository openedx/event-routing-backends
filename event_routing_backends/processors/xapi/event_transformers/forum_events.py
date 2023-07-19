"""
Transformers for forum related events.
"""
from django.conf import settings
from tincan import Activity, ActivityDefinition, LanguageMap, Verb

from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer


class BaseForumThreadTransformer(XApiTransformer):
    """
    Base transformer for forum thread events.
    """

    def get_object(self):
        """
        Get object for xAPI transformed event related to a thread.

        Returns:
            `Activity`
        """

        object_id = self.get_data('data.id', True)
        object_path = self.get_data('context.path', True).rstrip('/').replace(object_id, '').rstrip('/')

        return Activity(
            id='{lms_root_url}/{object_path}/{object_id}'.format(
                    lms_root_url=settings.LMS_ROOT_URL,
                    object_path=object_path,
                    object_id=object_id
                ),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_DISCUSSION,
            )
        )


@XApiTransformersRegistry.register('edx.forum.thread.created')
class ThreadCreatedTransformer(BaseForumThreadTransformer):
    """
    Transformers for event generated when learner creates a thread in discussion forum.
    """
    verb = Verb(
        id=constants.XAPI_VERB_POSTED,
        display=LanguageMap({constants.EN: constants.POSTED}),
    )

    def get_context_extensions(self):
        """
        Get extensions for thread created event context.

        Returns:
            `Extensions`
        """
        extensions = super().get_context_extensions()
        extensions.update({
            constants.XAPI_ACTIVITY_MODE: self.get_data('thread_type')
        })
        return extensions


@XApiTransformersRegistry.register('edx.forum.thread.edited')
class ThreadEditedTransformer(BaseForumThreadTransformer):
    """
    Transformers for event generated when learner modifies a thread in discussion forum.
    """
    verb = Verb(
        id=constants.XAPI_VERB_EDITED,
        display=LanguageMap({constants.EN: constants.EDITED}),
    )


@XApiTransformersRegistry.register('edx.forum.thread.viewed')
class ThreadViewedTransformer(BaseForumThreadTransformer):
    """
    Transformers for event generated when learner viewes a thread in discussion forum.
    """
    verb = Verb(
        id=constants.XAPI_VERB_VIEWED,
        display=LanguageMap({constants.EN: constants.VIEWED}),
    )


@XApiTransformersRegistry.register('edx.forum.thread.deleted')
class ThreadDeletedTransformer(BaseForumThreadTransformer):
    """
    Transformers for event generated when learner deletes a thread in discussion forum.
    """
    verb = Verb(
        id=constants.XAPI_VERB_DELETED,
        display=LanguageMap({constants.EN: constants.DELETED}),
    )


@XApiTransformersRegistry.register('edx.forum.thread.voted')
class ThreadVotedTransformer(BaseForumThreadTransformer):
    """
    Transformers for event generated when learner votes on a thread in discussion forum.
    """
    verb = Verb(
        id=constants.XAPI_VERB_VOTED,
        display=LanguageMap({constants.EN: constants.VOTED}),
    )

    def get_context_extensions(self):
        """
        Get extensions for thread voted event context.

        Returns:
            `Extensions`
        """
        extensions = super().get_context_extensions()
        extensions.update({
            constants.XAPI_ACTIVITY_MODE: self.get_data('vote_value')
        })
        return extensions
