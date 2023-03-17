"""
Transformers for problem interaction events.
"""
from event_routing_backends.helpers import get_anonymous_user_id, get_problem_block_id
from event_routing_backends.processors.caliper.registry import CaliperTransformersRegistry
from event_routing_backends.processors.caliper.transformer import CaliperTransformer

EVENT_ACTION_MAP = {
    'problem_check': 'Submitted',
    'problem_check_server': 'Graded',
    'edx.grades.problem.submitted': 'Submitted',
    'showanswer': 'Viewed',
    'problem_show': 'Viewed',
    'edx.problem.hint.demandhint_displayed': 'Viewed',
    'edx.problem.completed': 'Completed'
}

OBJECT_TYPE_MAP = {
    'problem_check': 'Assessment',
    'problem_check_server': 'Attempt',
    'edx.grades.problem.submitted': 'Assessment',
    'showanswer': 'Annotation',
    'problem_show': 'Frame',
    'edx.problem.hint.demandhint_displayed': 'Annotation',
    'edx.problem.completed': 'AssessmentItem'
}

OBJECT_NAME_MAP = {
    'problem_check': None,
    'problem_check_server': None,
    'edx.grades.problem.submitted': None,
    'showanswer': 'Solution',
    'problem_show': None,
    'edx.problem.hint.demandhint_displayed': 'Hint',
    'edx.problem.completed': None
}

EVENT_TYPE_MAP = {
    'problem_check': 'AssessmentEvent',
    'problem_check_server': 'GradeEvent',
    'edx.grades.problem.submitted': 'AssessmentEvent',
    'showanswer': 'Event',
    'problem_show': 'ViewEvent',
    'edx.problem.hint.demandhint_displayed': 'Event',
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
    additional_fields = ('generated',)

    def get_event_name_key(self):
        """
        Return event name key.

        Returns:
            str
        """
        key = self.get_data('name', True)
        if key == 'problem_check' and self.get_data('context.event_source') == 'server':
            key = 'problem_check_server'

        return key

    def get_generated(self):
        """
        Add all generated information related to `scores`.
        """
        if self.get_event_name_key() == 'problem_check_server':
            return {
                'score': {
                    'id': '_:score',
                    'type': 'Score',
                    'maxScore': self.get_data('max_grade'),
                    'scoreGiven': self.get_data('grade'),
                    'attempts': self.get_data('attempts'),
                    'extensions': {'success': "True" if self.get_data('success') == 'correct' else "False"},
                }
            }

        return None

    def get_type(self):
        """
        Return type for caliper event.

        Returns:
            str
        """

        return EVENT_TYPE_MAP[self.get_event_name_key()]

    def get_action(self):
        """
        Return action for caliper event.

        Returns:
            str
        """

        return EVENT_ACTION_MAP[self.get_event_name_key()]

    def get_object(self):
        """
        Return transformed object for caliper event.

        Returns:
            dict
        """
        self.backend_name = 'caliper'
        object_id = None
        event_data = None
        data = self.get_data('data')
        if data and isinstance(data, dict):
            event_data = data
            object_id = event_data.get('problem_id', event_data.get('module_id', None))

        if not object_id:
            object_id = get_problem_block_id(
                self.get_data('context.referer', True),
                self.get_data('data'),
                self.get_data('context.course_id')
            )
        key = self.get_event_name_key()

        anonymous_user_id = get_anonymous_user_id(self.extract_username_or_userid(), 'CALIPER')
        if key == 'showanswer':
            iri_url = '{}/solution'.format(object_id)
        elif key == 'edx.problem.hint.demandhint_displayed':
            iri_url = '{}/hint/{}'.format(object_id, event_data.get('hint_index', ''))
        elif key == 'problem_check_server':
            iri_url = '{}/user/{}/attempt/{}'.format(
                object_id,
                anonymous_user_id,
                str(event_data.get('attempts', ''))
            )
        else:
            iri_url = object_id

        caliper_object = self.transformed_event['object']
        caliper_object.update({
            'id': self.get_object_iri('xblock', iri_url),
            'type': OBJECT_TYPE_MAP.get(key, 'Attempt'),
            'name': OBJECT_NAME_MAP.get(key, None),
        })

        if key == 'problem_check_server':
            extensions = caliper_object['extensions']
            extensions['assignee'] = {}
            extensions['assignee']['id'] = self.get_object_iri(
                'user',
                anonymous_user_id
            )
            extensions['assignee']['type'] = 'Person'
            extensions['assignable'] = {}
            extensions['assignable']['id'] = self.get_object_iri('xblock', object_id)
            extensions['assignable']['type'] = 'Assessment'
            extensions['count'] = event_data.get('attempts', '')
            caliper_object['extensions'].update(extensions)

        return caliper_object
