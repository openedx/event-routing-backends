"""
Transformers for navigation related events.
"""
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

OBJECT_TYPE_MAP = {
    'edx.ui.lms.sequence.next_selected': 'DigitalResourceCollection',
    'edx.ui.lms.sequence.previous_selected': 'DigitalResourceCollection',
    'edx.ui.lms.sequence.tab_selected': 'DigitalResourceCollection',
    'edx.ui.lms.link_clicked': 'Webpage',
    'edx.ui.lms.sequence.outline.selected': 'DigitalResource',
    'edx.ui.lms.outline.selected': 'DigitalResource'
}


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
        self.backend_name = 'caliper'
        caliper_object = self.transformed_event['object']

        data = self.get_data('data')
        extensions = {}
        event_name = self.get_data('name', True)
        if event_name in (
            'edx.ui.lms.link_clicked',
            'edx.ui.lms.outline.selected'
        ):
            object_id = self.get_data('data.target_url', True)
            object_name = self.get_data('data.target_name')
        else:
            object_id = self.get_object_iri('xblock', self.get_data('data.id', True))
            object_name = 'Unit'
            data.pop('id')
            extensions['tab_count'] = self.get_data('data.tab_count')
            extensions['current_tab'] = self.get_data('data.current_tab')
            if event_name == 'edx.ui.lms.sequence.next_selected':
                extensions['target'] = "next unit"
            elif event_name == 'edx.ui.lms.sequence.previous_selected':
                extensions['target'] = 'previous unit'
            else:
                extensions['target'] = self.get_data('data.target_tab')

        caliper_object.update({
            'id': object_id,
            'type': OBJECT_TYPE_MAP.get(event_name, 'Webpage'),
            'name': object_name
        })

        caliper_object.pop('extensions', None)
        course_id = self.get_data('context.course_id')
        if course_id:
            extensions['isPartOf'] = {}
            extensions['isPartOf']['id'] = self.get_object_iri('course', course_id)
            extensions['isPartOf']['type'] = 'CourseOffering'

        if extensions:
            caliper_object.update({'extensions': extensions})

        return caliper_object
