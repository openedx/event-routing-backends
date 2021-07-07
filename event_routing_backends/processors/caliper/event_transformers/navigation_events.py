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
        self.event_version = 1.0
        self.backend_name = 'caliper'
        caliper_object = self.transformed_event['object']

        data = self.get_data('data')
        if self.get_data('name', True) in (
            'edx.ui.lms.link_clicked',
            'edx.ui.lms.outline.selected'
        ):
            object_id = self.get_data('data.target_url', True)
        else:
            object_id = self.get_data('data.id', True)
            data.pop('id')

        caliper_object.update({
            'id': object_id,
            'type': 'WebPage',
        })

        caliper_object.pop('extensions', None)

        extensions = self.extract_subdict_by_keys(data, ['current_tab', 'tab_count', 'target_tab', 'widget_placement'])
        if extensions:
            caliper_object.update({'extensions': extensions})

        return caliper_object
