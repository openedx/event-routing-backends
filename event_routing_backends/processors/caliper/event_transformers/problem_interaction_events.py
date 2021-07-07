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
        return EVENT_TYPE_MAP[self.get_data('name', True)]

    def get_action(self):
        """
        Return action for caliper event.

        Returns:
            str
        """
        return EVENT_ACTION_MAP[self.get_data('name', True)]

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        self.event_version = 1.0
        self.backend_name = 'caliper'
        object_id = None
        event_data = None
        data = self.get_data('data')
        if data and isinstance(data, dict):
            event_data = data
            object_id = event_data.get('problem_id', event_data.get('module_id', None))

        if not object_id:
            object_id = get_block_id_from_event_referrer(self.get_data('context.referer', True))

        caliper_object = self.transformed_event['object']
        caliper_object.update({
            'id': object_id,
            'type': OBJECT_TYPE_MAP[self.get_data('name', True)],
        })

        if event_data and isinstance(event_data, dict):
            extensions = self.extract_subdict_by_keys(
                event_data, [
                    'module_id',
                    'grade',
                    'max_grade',
                    'success',
                    'attempts',
                    'event_transaction_id',
                    'event_transaction_type',
                    'weighted_earned',
                    'weighted_possible',
                ]
            )
            caliper_object['extensions'].update(extensions)

        return caliper_object
