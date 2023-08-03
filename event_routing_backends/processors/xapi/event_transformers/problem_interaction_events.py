"""
Transformers for problem interaction events.
"""
from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Result

from event_routing_backends.helpers import get_problem_block_id
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.transformer import XApiTransformer, XApiVerbTransformerMixin

# map open edx problems interation types to xAPI valid interaction types
INTERACTION_TYPES_MAP = {
    'choiceresponse': 'choice',
    'multiplechoiceresponse': 'choice',
    'numericalresponse': 'numeric',
    'stringresponse': 'fill-in',
    'customresponse': 'other',
    'coderesponse': 'other',
    'externalresponse': 'other',
    'formularesponse': 'fill-in',
    'schematicresponse': 'other',
    'imageresponse': 'matching',
    'annotationresponse': 'fill-in',
    'choicetextresponse': 'choice',
    'optionresponse': 'choice',
    'symbolicresponse': 'fill-in',
    'truefalseresponse': 'true-false',
    'non_existent': 'other',
}
EVENT_OBJECT_DEFINITION_TYPE = {
    'edx.grades.problem.submitted': constants.XAPI_ACTIVITY_QUESTION,
    'showanswer': constants.XAPI_ACTIVITY_SOLUTION,
    'edx.problem.hint.demandhint_displayed': constants.XAPI_ACTIVITY_SUPPLEMENTAL_INFO,
}


DEFAULT_INTERACTION_TYPE = 'other'

VERB_MAP = {
    'edx.grades.problem.submitted': {
        'id': constants.XAPI_VERB_ATTEMPTED,
        'display': constants.ATTEMPTED
    },
    'problem_check_browser': {
        'id': constants.XAPI_VERB_ATTEMPTED,
        'display': constants.ATTEMPTED
    },
    'problem_check': {
        'id': constants.XAPI_VERB_EVALUATED,
        'display': constants.EVALUATED
    },
    'showanswer': {
        'id': constants.XAPI_VERB_ASKED,
        'display': constants.ASKED
    },
    'edx.problem.hint.demandhint_displayed': {
        'id': constants.XAPI_VERB_ASKED,
        'display': constants.ASKED
    },
    'edx.problem.completed': {
        'id': constants.XAPI_VERB_COMPLETED,
        'display': constants.COMPLETED
    },
}


class BaseProblemsTransformer(XApiTransformer, XApiVerbTransformerMixin):
    """
    Base Transformer for problem interaction events.
    """
    verb_map = VERB_MAP

    def get_object(self):
        """
        Get object for xAPI transformed event.
        Returns:
            `Activity`
        """
        object_id = None
        data = self.get_data('data')
        if data and isinstance(data, dict):
            object_id = self.get_data('data.problem_id') or self.get_data('data.module_id', True)

        event_name = self.get_data('name', True)

        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=EVENT_OBJECT_DEFINITION_TYPE[event_name] if event_name in EVENT_OBJECT_DEFINITION_TYPE else
                constants.XAPI_ACTIVITY_INTERACTION,
            ),
        )


@XApiTransformersRegistry.register('showanswer')
@XApiTransformersRegistry.register('edx.problem.completed')
@XApiTransformersRegistry.register('edx.problem.hint.demandhint_displayed')
class ProblemEventsTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction events into xAPI format.
    """

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        xapi_object = super().get_object()
        event_name = self.get_data('name', True)
        if event_name == 'showanswer':
            problem_id = self.get_data('problem_id', True)
            xapi_object.id = '{iri}/answer'.format(
                iri=self.get_object_iri('xblock', problem_id),
            )
        if event_name == 'edx.problem.hint.demandhint_displayed':
            module_id = self.get_data('module_id', True)
            hint_index = self.get_data('hint_index', True)
            xapi_object.id = '{iri}/hint/{hint_index}'.format(
                iri=self.get_object_iri('xblock', module_id),
                hint_index=hint_index
            )

        return xapi_object


@XApiTransformersRegistry.register('edx.grades.problem.submitted')
class ProblemSubmittedTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('result', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        xapi_object = super().get_object()
        xapi_object.id = self.get_object_iri('xblock', xapi_object.id)
        return xapi_object

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_data = self.get_data('data')
        weighted_possible = event_data['weighted_possible'] or 0
        weighted_earned = event_data['weighted_earned'] or 0

        if weighted_possible > 0:
            scaled = weighted_earned/weighted_possible
        else:
            scaled = 0
        return Result(
            success=weighted_earned >= weighted_possible,
            score={
                'min': 0,
                'max': weighted_possible,
                'raw': weighted_earned,
                'scaled': scaled
            }
        )


@XApiTransformersRegistry.register('problem_check')
class ProblemCheckTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('result', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        xapi_object = super().get_object()

        # If the event was generated from browser, there is no `problem_id`
        # or `module_id` field. Therefore we get block id from the referrer.
        event_source = self.get_data('context.event_source') or self.get_data('event_source')
        referer = self.get_data('referer') or self.get_data('context.referer', True)
        if event_source == 'browser':
            block_id = get_problem_block_id(
                referer,
                self.get_data('data'),
                self.get_data('context.course_id')
            )
            xapi_object.id = self.get_object_iri('xblock', block_id)
            return xapi_object
        else:
            if xapi_object.id:
                xapi_object.id = self.get_object_iri('xblock', xapi_object.id)

        if self.get_data('data.attempts'):
            xapi_object.definition.extensions = Extensions({
                constants.XAPI_ACTIVITY_ATTEMPT: self.get_data('data.attempts')
            })
        interaction_type = self._get_interaction_type()
        submission = self._get_submission()
        if submission:
            interaction_type = INTERACTION_TYPES_MAP[submission['response_type']]
            xapi_object.definition.description = LanguageMap({constants.EN_US: submission['question']})

        xapi_object.definition.interaction_type = interaction_type

        return xapi_object

    def _get_submission(self):
        """
        Return first submission available in event data

        Returns:
            dict
        """
        submissions = self.get_data('data.submission')
        if submissions:
            for sub_id in submissions:
                if 'response_type' in submissions[sub_id] and submissions[sub_id]['response_type']:
                    return submissions[sub_id]

        return None

    def _get_interaction_type(self):
        """
        Convert the Open edX's events response type into xAPI supported
        interaction type.

        Return "other" if the mapping does not exist for the event.

        Returns:
            str
        """
        response_type = self.get_data('response_type')
        try:
            return INTERACTION_TYPES_MAP[response_type]
        except KeyError:
            return DEFAULT_INTERACTION_TYPE

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            Result
        """
        # Do not transform result if the event is generated from browser
        source = self.get_data('event_source') or self.get_data('context.event_source')
        if source == 'browser':
            return None

        event_data = self.get_data('data')
        if event_data is None:
            event_data = {}

        submission = self._get_submission()
        if submission:
            response = submission["answer"]
        else:
            response = event_data.get('answers', None)

        max_grade = event_data.get('max_grade', None)
        grade = event_data.get('grade', None)
        scaled = None

        if max_grade is not None and grade is not None:
            if max_grade > 0:
                scaled = grade / max_grade
            else:
                scaled = 0

        return Result(
            success=event_data.get('success', None) == 'correct',
            score={
                'min': 0,
                'max': max_grade,
                'raw': grade,
                'scaled': scaled,
            },
            response=response
        )
