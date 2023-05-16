"""
Transformers for video interaction events.

NOTE: Currently Open edX only emits legacy events for video interaction i.e.
- load_video
- play_video
- stop_video
- complete_video
- pause_video
- seek_video
- hide_transcript
- show_transcript
- speed_change_video
- video_hide_cc_menu
- video_show_cc_menu

Currently, mobile apps emits these events using the new names but will be
added in edx-platform too. Therefore, we are adding support for legacy event names
as well as new names.

The (soon to be) updated event names are as following:
- edx.video.loaded
- edx.video.played
- edx.video.stopped
- edx.video.paused
- edx.video.position.changed
- edx.video.completed
- edx.video.transcript.hidden
- edx.video.transcript.shown
- edx.video.closed_captions.hidden
- edx.video.closed_captions.shown
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
    'hide_transcript': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'edx.video.transcript.hidden': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'show_transcript': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'edx.video.transcript.shown': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'speed_change_video': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'video_hide_cc_menu': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'video_show_cc_menu': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'edx.video.closed_captions.hidden': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
    'edx.video.closed_captions.shown': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
    },
}


class BaseVideoTransformer(XApiTransformer, XApiVerbTransformerMixin):
    """
    Base transformer for video interaction events.
    """
    verb_map = VERB_MAP

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
        current_time = self.get_data('data.current_time') or self.get_data('data.currentTime')
        return Result(
            extensions=Extensions({
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_float(current_time)
            })
        )


@XApiTransformersRegistry.register('hide_transcript')
@XApiTransformersRegistry.register('video_hide_cc_menu')
@XApiTransformersRegistry.register('edx.video.transcript.hidden')
@XApiTransformersRegistry.register('show_transcript')
@XApiTransformersRegistry.register('edx.video.transcript.shown')
@XApiTransformersRegistry.register('edx.video.closed_captions.hidden')
@XApiTransformersRegistry.register('edx.video.closed_captions.shown')
@XApiTransformersRegistry.register('video_show_cc_menu')
class VideoCCTransformers(BaseVideoTransformer):
    """
    Transformer for the events generated when CC enabled/disabled on videos
    """
    additional_fields = BaseVideoTransformer.additional_fields + ('result', )

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_name = self.get_data('name')
        cc_enabled = bool(
            event_name in [
                'edx.video.closed_captions.shown',
                'edx.video.transcript.shown',
                'video_show_cc_menu',
                'show_transcript',
            ]
         )
        current_time = self.get_data('data.current_time') or self.get_data('data.currentTime')

        return Result(
            extensions=Extensions({
                constants.XAPI_RESULT_VIDEO_TIME: convert_seconds_to_float(current_time),
                constants.XAPI_RESULT_VIDEO_CC_ENABLED: cc_enabled
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


@XApiTransformersRegistry.register('speed_change_video')
class VideoSpeedChangedTransformer(BaseVideoTransformer):
    """
    Transformer for the events generated when speed of video is changed.
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
                constants.XAPI_RESULT_VIDEO_SPEED_FROM: ''.join([self.get_data('data.old_speed'), 'x']),
                constants.XAPI_RESULT_VIDEO_SPEED_TO: ''.join([self.get_data('data.new_speed'), 'x']),
            }),
        )
