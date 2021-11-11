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

from django.conf import settings
from tincan import Activity, ActivityDefinition, Extensions, Result

from event_routing_backends.helpers import convert_seconds_to_float, make_video_block_id
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer, XApiVerbTransformerMixin

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
    verb_map = VERB_MAP
    event_version = "1.0"

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        course_id = self.get_data('context.course_id', True)

        video_id = self.get_data('data.id', True)

        object_id = make_video_block_id(course_id=course_id, video_id=video_id)

        return Activity(
            id='{lms_root_url}/xblock/{object_id}'.format(
                    lms_root_url=settings.LMS_ROOT_URL,
                    object_id=object_id
                ),
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_VIDEO,
                # TODO: Add video's display name
            ),
        )

    def get_context_extensions(self):
        """
        Get extensions for xAPI transformed event Context.

        Returns:
            `Extensions`
        """

        extensions = super().get_context_extensions()
        extensions.update({
                # TODO: Add completion threshold once its added in the platform.
                constants.XAPI_CONTEXT_VIDEO_LENGTH: convert_seconds_to_float(self.get_data('data.duration'))
            })
        return extensions


@XApiTransformersRegistry.register('load_video')
@XApiTransformersRegistry.register('edx.video.loaded')
class VideoLoadedTransformer(BaseVideoTransformer):
    """
    Transformer for the event generated when a video is loaded in the browser.
    """


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
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_float(self.get_data('data.currentTime'))
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
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_float(self.get_data('data.duration'))
            }),
            completion=True,
            duration=convert_seconds_to_float(self.get_data('data.duration'))
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
                constants.XAPI_RESULT_VIDEO_TIME_FROM: convert_seconds_to_float(self.get_data('data.old_time')),
                constants.XAPI_RESULT_VIDEO_TIME_TO: convert_seconds_to_float(self.get_data('data.new_time')),
            }),
        )
