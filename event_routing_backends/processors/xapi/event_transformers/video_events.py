"""
Transformers for video interaction events.

NOTE: Currently Open edX only emits legacy events for video interaction i.e.
- load_video
- play_video
- stop_video
- complete_video (proposed)
- pause_video
- seek_video

Currently, mobile apps emits these events using the new names but will be
added in edx-platform too. Therefore, we are adding support for legacy event names
as well as new names.

The (soon to be) updated event names are as following:
- edx.video.loaded
- edx.video.played
- edx.video.stopped
- edx.video.paused
- edx.video.position.changed
- edx.video.completed (proposed)
"""
from logging import getLogger

from tincan import (
    Activity,
    ActivityDefinition,
    ActivityList,
    Context,
    ContextActivities,
    Extensions,
    LanguageMap,
    Result,
)

from event_routing_backends.helpers import (
    convert_seconds_to_iso,
    get_anonymous_user_id_by_username,
    make_course_url,
    make_video_block_id,
)
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer, XApiVerbTransformerMixin

logger = getLogger(__name__)


VERB_MAP = {
    'load_video': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    },
    'edx.video.loaded': {
        'id': constants.XAPI_VERB_INITIALIZED,
        'display': constants.INITIALIZED
    },

    'play_video': {
        'id': constants.XAPI_VERB_PLAYED,
        'display': constants.PLAYED
    },
    'edx.video.played': {
        'id': constants.XAPI_VERB_PLAYED,
        'display': constants.PLAYED
    },

    'stop_video': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },
    'edx.video.stopped': {
        'id': constants.XAPI_VERB_TERMINATED,
        'display': constants.TERMINATED
    },

    'complete_video': {
        'id': constants.XAPI_VERB_COMPLETED,
        'display': constants.COMPLETED
    },
    'edx.video.completed': {
        'id': constants.XAPI_VERB_COMPLETED,
        'display': constants.COMPLETED
    },

    'pause_video': {
        'id': constants.XAPI_VERB_PAUSED,
        'display': constants.PAUSED
    },
    'edx.video.paused': {
        'id': constants.XAPI_VERB_PAUSED,
        'display': constants.PAUSED
    },

    'seek_video': {
        'id': constants.XAPI_VERB_SEEKED,
        'display': constants.SEEKED
    },
    'edx.video.position.changed': {
        'id': constants.XAPI_VERB_SEEKED,
        'display': constants.SEEKED
    },
}


class BaseVideoTransformer(XApiTransformer, XApiVerbTransformerMixin):
    """
    Base transformer for video interaction events.
    """
    additional_fields = ('context', )
    verb_map = VERB_MAP

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course_id = self.find_nested('course_id')
        video_id = self.event['data']['id']

        object_id = make_video_block_id(course_id=course_id, video_id=video_id)
        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_VIDEO,
                # TODO: how to get video's display name?
                name=LanguageMap({constants.EN: 'Video Display Name'}),
                extensions=Extensions({
                    'code': self.event['data']['code']
                })
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        return Context(
            registration=get_anonymous_user_id_by_username(
                self.event['context']['username']
            ),
            contextActivities=self.get_context_activities()
        )

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id=make_course_url(self.event['context']['course_id']),
                object_type=constants.XAPI_ACTIVITY_COURSE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
            category=Activity(
                id=constants.XAPI_ACTIVITY_VIDEO
            )
        )


@XApiTransformersRegistry.register('load_video')
@XApiTransformersRegistry.register('edx.video.loaded')
class VideoLoadedTransformer(BaseVideoTransformer):
    """
    Transformer for the event generated when a video is loaded in the browser.
    """

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """
        context = super().get_context()

        # TODO: Add completion threshold once its added in the platform.
        context.extensions = Extensions({
            constants.XAPI_CONTEXT_VIDEO_LENGTH: convert_seconds_to_iso(self.find_nested('duration')),
        })
        return context


@XApiTransformersRegistry.register('play_video')
@XApiTransformersRegistry.register('edx.video.played')
@XApiTransformersRegistry.register('stop_video')
@XApiTransformersRegistry.register('edx.video.stopped')
@XApiTransformersRegistry.register('pause_video')
@XApiTransformersRegistry.register('edx.video.paused')
class VideoInteractionTransformers(BaseVideoTransformer):
    """
    Transformer for the events generated when learner interacts with the video.
    """
    additional_fields = BaseVideoTransformer.additional_fields + ('result', )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        return Result(
            extensions=Extensions({
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_iso(self.find_nested('currentTime'))
            })
        )


@XApiTransformersRegistry.register('edx.video.completed')
@XApiTransformersRegistry.register('complete_video')
class VideoCompletedTransformer(BaseVideoTransformer):
    """
    Transformer for the events generated when learner completes any video.
    """
    additional_fields = BaseVideoTransformer.additional_fields + ('result', )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        return Result(
            extensions=Extensions({
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_iso(self.find_nested('duration'))
            }),
            completion=True,
            duration=convert_seconds_to_iso(self.find_nested('duration'))
        )


@XApiTransformersRegistry.register('seek_video')
@XApiTransformersRegistry.register('edx.video.position.changed')
class VideoPositionChangedTransformer(BaseVideoTransformer):
    """
    Transformer for the events generated when changes the position of any video.
    """
    additional_fields = BaseVideoTransformer.additional_fields + ('result', )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        return Result(
            extensions=Extensions({
                constants.XAPI_RESULT_VIDEO_TIME_FROM: convert_seconds_to_iso(self.find_nested('old_time')),
                constants.XAPI_RESULT_VIDEO_TIME_TO: convert_seconds_to_iso(self.find_nested('new_time')),
            }),
        )
