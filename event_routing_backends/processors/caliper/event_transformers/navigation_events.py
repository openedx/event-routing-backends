"""
Transformers for navigation related events.
"""
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer


@CaliperTransformersRegistry.register('edx.ui.lms.sequence.next_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.previous_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.tab_selected')
@CaliperTransformersRegistry.register('edx.ui.lms.link_clicked')
@CaliperTransformersRegistry.register('edx.ui.lms.sequence.outline.selected')
@CaliperTransformersRegistry.register('edx.ui.lms.outline.selected')
class NavigationEventsTransformers(CaliperTransformer):
    """
    These events are generated when the user navigates through
    the units in a course.

    "edx.ui.lms.sequence.outline.selected" and "edx.ui.lms.outline.selected" are
    actually same events.
    """
    action = 'NavigatedTo'
    type = 'NavigationEvent'

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        caliper_object = self.transformed_event['object']
        data = self.event['data'].copy()

        object_id = data.pop('target_url') if self.event['name'] in (
            'edx.ui.lms.link_clicked',
            'edx.ui.lms.outline.selected'
        ) else data.pop('id')

        caliper_object.update({
            'id': object_id,
            'type': 'WebPage',
            'extensions': data
        })

        return caliper_object
