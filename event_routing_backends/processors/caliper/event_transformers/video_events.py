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
from datetime import timedelta

from isodate import duration_isoformat

from event_routing_backends.helpers import convert_seconds_to_iso, make_video_block_id
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

EVENTS_ACTION_MAP = {
    'load_video': 'Retrieved',
    'edx.video.loaded': 'Retrieved',

    'play_video': 'Started',
    'edx.video.played': 'Started',

    'stop_video': 'Ended',
    'edx.video.stopped': 'Ended',

    'complete_video': 'Ended',
    'edx.video.completed': 'Ended',

    'pause_video': 'Paused',
    'edx.video.paused': 'Paused',

    'seek_video': 'JumpedTo',
    'edx.video.position.changed': 'JumpedTo',
}


class BaseVideoTransformer(CaliperTransformer):
    """
    Base transformer for video interaction events.
    """
    type = 'MediaEvent'

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
            str
        """
        self.event_version = 1.0
        self.backend_name = 'caliper'
        caliper_object = self.transformed_event['object']
        data = self.get_data('data')
        course_id = self.get_data('context.course_id', True)
        video_id = self.get_data('data.id', True)
        object_id = make_video_block_id(course_id=course_id, video_id=video_id)

        caliper_object.update({
            'id': object_id,
            'type': 'VideoObject',
            'duration': duration_isoformat(timedelta(
                    seconds=data.get('duration', 0)
            ))
        })
        caliper_object['extensions'] = {'course_id': course_id}
        extensions = self.extract_subdict_by_keys(
            data, ['id', 'new_time', 'old_time', 'currentTime']
        )

        if 'currentTime' in extensions:
            extensions['currentTime'] = convert_seconds_to_iso(extensions['currentTime'])
        if 'new_time' in extensions:
            extensions['new_time'] = convert_seconds_to_iso(seconds=extensions['new_time'])
        if 'old_time' in extensions:
            extensions['old_time'] = convert_seconds_to_iso(seconds=extensions['old_time'])
        caliper_object['extensions'].update(extensions)

        return caliper_object


@CaliperTransformersRegistry.register('load_video')
@CaliperTransformersRegistry.register('edx.video.loaded')
class LoadVideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is loaded.
    """
    type = 'Event'


@CaliperTransformersRegistry.register('stop_video')
@CaliperTransformersRegistry.register('edx.video.stopped')
@CaliperTransformersRegistry.register('complete_video')
@CaliperTransformersRegistry.register('edx.video.completed')
class StopVideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is completed.

    Please note that "complete_video" doesn't exist currently but is
    expected to be added.
    """


@CaliperTransformersRegistry.register('play_video')
@CaliperTransformersRegistry.register('edx.video.played')
@CaliperTransformersRegistry.register('pause_video')
@CaliperTransformersRegistry.register('edx.video.paused')
class PlayPauseVideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is played or paused.
    """
    additional_fields = ('target', )

    def get_object(self):
        """
        Return transformed object for the caliper event.

        Returns:
            dict
        """
        caliper_object = super().get_object()

        # currentTime is included in the `target` of transformed event
        # therefore no need to include it in the `extensions`.
        caliper_object['extensions'].pop('currentTime', None)

        return caliper_object

    def get_target(self):
        """
        Return target for the caliper event.

        Returns:
            str
        """
        current_time = convert_seconds_to_iso(
            seconds=self.get_data('data.currentTime')
        )

        return {
            'id': self.transformed_event['object']['id'],
            'type': 'MediaLocation',
            'currentTime': current_time
        }


@CaliperTransformersRegistry.register('seek_video')
@CaliperTransformersRegistry.register('edx.video.position.changed')
class SeekVideoTransformer(BaseVideoTransformer):
    """
    Transform the events fired when a video is seeked.
    """
