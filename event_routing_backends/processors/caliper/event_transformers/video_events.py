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
from event_routing_backends.helpers import convert_seconds_to_iso, make_video_block_id
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

EVENTS_ACTION_MAP = {
    'load_video': 'Started',
    'edx.video.loaded': 'Started',

    'play_video': 'Resumed',
    'edx.video.played': 'Resumed',

    'stop_video': 'Ended',
    'edx.video.stopped': 'Ended',

    'complete_video': 'Ended',
    'edx.video.completed': 'Ended',

    'pause_video': 'Paused',
    'edx.video.paused': 'Paused',

    'seek_video': 'JumpedTo',
    'edx.video.position.changed': 'JumpedTo',

    'hide_transcript': 'DisabledClosedCaptioning',
    'edx.video.transcript.hidden': 'DisabledClosedCaptioning',
    'edx.video.closed_captions.hidden': 'DisabledClosedCaptioning',
    'video_hide_cc_menu': 'DisabledClosedCaptioning',

    'show_transcript': 'EnabledClosedCaptioning',
    'edx.video.transcript.shown': 'EnabledClosedCaptioning',
    'edx.video.closed_captions.shown': 'EnabledClosedCaptioning',
    'video_show_cc_menu': 'EnabledClosedCaptioning',

    'speed_change_video': 'ChangedSpeed',
}


class BaseVideoTransformer(CaliperTransformer):
    """
    Base transformer for video interaction events.
    """
    type = 'MediaEvent'
    additional_fields = ('target',)

    def get_action(self):
        """
        Return action for the caliper event.

        Returns:
            str
        """
        return EVENTS_ACTION_MAP[self.get_data('name', True)]

    def get_object(self):
        """
        Return object for the caliper event.

        Returns:
            dict
        """
        self.backend_name = 'caliper'
        caliper_object = self.transformed_event['object']
        data = self.get_data('data')
        course_id = self.get_data('context.course_id', True)
        video_id = self.get_data('data.id', True)
        object_id = make_video_block_id(course_id=course_id, video_id=video_id)

        caliper_object.update({
            'id': self.get_object_iri('xblock', object_id),
            'type': 'VideoObject',
            'duration': convert_seconds_to_iso(
                seconds=data.get('duration', 0)
            )
        })

        return caliper_object

    def get_target(self):
        """
        Return target for the caliper event.

        Returns:
            dict
        """

        current_time = convert_seconds_to_iso(
            seconds=self.get_data('data.currentTime') or self.get_data('data.current_time')
        )

        return {
            'id': '_:MediaLocation',
            'type': 'MediaLocation',
            'currentTime': current_time
        }


@CaliperTransformersRegistry.register('load_video')
@CaliperTransformersRegistry.register('edx.video.loaded')
@CaliperTransformersRegistry.register('stop_video')
@CaliperTransformersRegistry.register('edx.video.stopped')
@CaliperTransformersRegistry.register('complete_video')
@CaliperTransformersRegistry.register('edx.video.completed')
@CaliperTransformersRegistry.register('play_video')
@CaliperTransformersRegistry.register('edx.video.played')
@CaliperTransformersRegistry.register('pause_video')
@CaliperTransformersRegistry.register('edx.video.paused')
@CaliperTransformersRegistry.register('hide_transcript')
@CaliperTransformersRegistry.register('edx.video.transcript.hidden')
@CaliperTransformersRegistry.register('edx.video.closed_captions.hidden')
@CaliperTransformersRegistry.register('video_hide_cc_menu')
@CaliperTransformersRegistry.register('show_transcript')
@CaliperTransformersRegistry.register('edx.video.transcript.shown')
@CaliperTransformersRegistry.register('edx.video.closed_captions.shown')
@CaliperTransformersRegistry.register('video_show_cc_menu')
class VideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is loaded.
    """


@CaliperTransformersRegistry.register('seek_video')
@CaliperTransformersRegistry.register('edx.video.position.changed')
class SeekVideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is seeked.
    """

    def get_target(self):
        """
        Return target location for the caliper event.

        Returns:
            dict
        """
        target = super().get_target()
        current_time = convert_seconds_to_iso(
            seconds=self.get_data('data.currentTime') or self.get_data('data.old_time')
        )
        new_time = convert_seconds_to_iso(
            seconds=self.get_data('data.new_time')
        )
        target.update({
            'currentTime': current_time,
            'extensions': {
                'newTime': new_time,
            }
        })
        return target


@CaliperTransformersRegistry.register('speed_change_video')
class VideoSpeedChangedTransformer(BaseVideoTransformer):
    """
    Transform the event fired when a video's speed is changed.
    """
    additional_fields = ('target', 'extensions',)

    def get_extensions(self):
        return {
            'oldSpeed': self.get_data('old_speed'),
            'newSpeed': self.get_data('new_speed'),
        }
