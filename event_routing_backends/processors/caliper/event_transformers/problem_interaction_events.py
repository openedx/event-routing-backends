"""
Transformers for problem interaction events.
"""
from event_routing_backends.helpers import get_block_id_from_event_referrer
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

EVENT_ACTION_MAP = {
    'problem_check': 'Submitted',
    'edx.grades.problem.submitted': 'Submitted',
    'showanswer': 'Viewed',
    'problem_show': 'Viewed',
    'edx.problem.hint.demandhint_displayed': 'Viewed',
    'edx.problem.completed': 'Completed'
}

OBJECT_TYPE_MAP = {
    'problem_check': 'Assessment',
    'edx.grades.problem.submitted': 'Assessment',
    'showanswer': 'Frame',
    'problem_show': 'Frame',
    'edx.problem.hint.demandhint_displayed': 'Frame',
    'edx.problem.completed': 'AssessmentItem'
}

EVENT_TYPE_MAP = {
    'problem_check': 'AssessmentEvent',
    'edx.grades.problem.submitted': 'AssessmentEvent',
    'showanswer': 'ViewEvent',
    'problem_show': 'ViewEvent',
    'edx.problem.hint.demandhint_displayed': 'ViewEvent',
    'edx.problem.completed': 'AssessmentItemEvent'
}


@CaliperTransformersRegistry.register('problem_check')
@CaliperTransformersRegistry.register('edx.grades.problem.submitted')
@CaliperTransformersRegistry.register('showanswer')
@CaliperTransformersRegistry.register('edx.problem.hint.demandhint_displayed')
@CaliperTransformersRegistry.register('edx.problem.completed')
class ProblemEventsTransformers(CaliperTransformer):
    """
    Transform problem interaction related events into caliper format.

    Currently there is no "edx.problem.completed" event in open edx but
    will be added in future as per the mapping document:
    https://docs.google.com/spreadsheets/u/1/d/1z_1IGFVDF-wZToKS2EGXFR3s0NXoh6tTKhEtDkevFEM/edit?usp=sharing.
    """

    def get_type(self):
        """
        Return type for caliper event.

        Returns:
            str
        """
        return EVENT_TYPE_MAP[self.event['name']]

    def get_action(self):
        """
        Return action for caliper event.

        Returns:
            str
        """
        return EVENT_ACTION_MAP[self.event['name']]

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        object_id = self.find_nested('problem_id')
        if not object_id:
            object_id = self.find_nested('module_id')
        if not object_id:
            object_id = get_block_id_from_event_referrer(self.event) or self.event['context']['referer']

        caliper_object = self.transformed_event['object']
        caliper_object.update({
            'id': object_id,
            'type': OBJECT_TYPE_MAP[self.event['name']],
        })

        if self.event['context'].get('event_source') == 'browser':
            caliper_object['extensions'].update({
                'data': self.event['data']
            })
        else:
            caliper_object['extensions'].update(self.event['data'])
            # problem_id is already being used as object id
            if 'problem_id' in caliper_object['extensions']:
                del caliper_object['extensions']['problem_id']

        if 'user_id' in caliper_object['extensions']:
            del caliper_object['extensions']['user_id']

        return caliper_object
