"""
Transformers for problem interaction events.
"""
from tincan import (
    Activity,
    ActivityDefinition,
    ActivityList,
    Context,
    ContextActivities,
    Extensions,
    InteractionComponent,
    InteractionComponentList,
    LanguageMap,
    Result,
)

from event_routing_backends.helpers import (
    get_anonymous_user_id_by_username,
    get_block_id_from_event_referrer,
    make_course_url,
)
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
    'coderesponse': 'performance',  # or "other"?
    'externalresponse': 'performance',  # or "other"?
    'formularesponse': 'fill-in',
    'schematicresponse': 'sequencing',  # or "other"?
    'imageresponse': 'matching',
    'annotationresponse': 'fill-in',
    'choicetextresponse': 'choice',
    'optionresponse': 'choice',
    'symbolicresponse': 'fill-in',
    'truefalseresponse': 'true-false',
}


DEFAULT_INTERACTION_TYPE = 'other'

VERB_MAP = {
    'edx.grades.problem.submitted': {
        'id': constants.XAPI_VERB_ATTEMPTED,
        'display': constants.ATTEMPTED
    },
    'problem_check': {
        'id': constants.XAPI_VERB_ANSWERED,
        'display': constants.ANSWERED
    },
    'showanswer': {
        'id': constants.XAPI_VERB_ASKED,
        'display': constants.ASKED
    },
    'edx.problem.hint.demandhint_displayed': {
        'id': constants.XAPI_VERB_INTERACTED,
        'display': constants.INTERACTED
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
    additional_fields = ('context', )
    verb_map = VERB_MAP
    event_version = 1.0

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        object_id = None
        data = self.get_data('data')
        if data and isinstance(data, dict):
            object_id = data.get('problem_id', data.get('module_id', None))

        # TODO: Add definition[name] of problem once it is added in the event.
        return Activity(
            id=object_id,
            definition=ActivityDefinition(
                type=constants.XAPI_ACTIVITY_INTERACTION,
            ),
        )

    def get_context(self):
        """
        Get context for xAPI transformed event.

        Returns:
            `Context`
        """

        context = Context(
            registration=get_anonymous_user_id_by_username(
                self.extract_username()
            ),
            contextActivities=self.get_context_activities()
        )
        context.extensions = Extensions({"eventVersion": self.event_version})
        return context

    def get_context_activities(self):
        """
        Get context activities for xAPI transformed event.

        Returns:
            `ContextActivities`
        """
        parent_activities = [
            Activity(
                id=make_course_url(self.get_data('context.course_id')),
                object_type=constants.XAPI_ACTIVITY_COURSE
            ),
        ]
        return ContextActivities(
            parent=ActivityList(parent_activities),
        )


@XApiTransformersRegistry.register('showanswer')
@XApiTransformersRegistry.register('edx.problem.completed')
@XApiTransformersRegistry.register('edx.problem.hint.demandhint_displayed')
class ProblemEventsTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction events into xAPI format.
    """


@XApiTransformersRegistry.register('edx.grades.problem.submitted')
class ProblemSubmittedTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('context', 'result')

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            `Result`
        """
        event_data = self.get_data('data')
        return Result(
            success=event_data['weighted_earned'] >= event_data['weighted_possible'],
            score={
                'min': 0,
                'max': event_data['weighted_possible'],
                'raw': event_data['weighted_earned'],
                'scaled': event_data['weighted_earned']/event_data['weighted_possible']
            }
        )


@XApiTransformersRegistry.register('problem_check')
class ProblemCheckTransformer(BaseProblemsTransformer):
    """
    Transform problem interaction related events into xAPI format.
    """
    additional_fields = ('context', 'result', )

    def get_object(self):
        """
        Get object for xAPI transformed event.

        Returns:
            `Activity`
        """
        xapi_object = super().get_object()

        # If the event was generated from browser, there is no `problem_id`
        # or `module_id` field. Therefore we get block id from the referrer.
        if self.get_data('context.event_source') == 'browser':
            xapi_object.id = get_block_id_from_event_referrer(self.get_data('context.referer', True))
            return xapi_object

        interaction_type = self._get_interaction_type()
        answers = self._get_answers_list()
        xapi_object.definition.interaction_type = interaction_type
        xapi_object.definition.correct_responses_pattern = answers

        if interaction_type == 'choice':
            xapi_object.definition.choices = self._get_choices_list()

        return xapi_object

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

    def _get_answers_list(self):
        """
        Get the answers list from the event.

        The event contains answers in the form of:

        {
            ...,
            "data": {
                "answers":{
                    "[id]": <Answer(s)>
                }

            }
        }

        Where these answer(s) can either be a single string, or a list of strings.

        Returns:
            list
        """
        answers = self.get_data('data.answers')
        if answers is None:
            answers = {}
        try:
            answers = next(iter(answers.values()))
            if isinstance(answers, str):
                return [answers]

            return answers
        except StopIteration:
            return []

    def _get_choices_list(self):
        """
        Return list of choices for the problem.

        Every choice is an InteractionComponent containing id (obtained from the
        `data[answers][<ID>]` map) and a correspoding display name (obtained from
        `data[submission][<ID>][answer]` map).

        These answer(s) could either be a single string or be a list of strings.

        Returns:
            InteractionComponentList<InteractionComponent>
        """
        answers = self._get_answers_list()
        answers_descriptions = self.get_data('answer')
        if isinstance(answers_descriptions, str):
            answers_descriptions = [answers_descriptions, ]
        return InteractionComponentList([
            InteractionComponent(
                id=answer,
                description=LanguageMap({constants.EN: description})
            ) for (answer, description) in zip(answers, answers_descriptions)
        ])

    def get_result(self):
        """
        Get result for xAPI transformed event.

        Returns:
            Result
        """
        # Do not transform result if the event is generated from browser
        if self.get_data('context.event_source') == 'browser':
            return None

        event_data = self.get_data('data')
        if event_data is None:
            event_data = {}
        return Result(
            success=event_data.get('success', None) == 'correct',
            score={
                'min': 0,
                'max': event_data.get('max_grade', None),
                'raw': event_data.get('grade', None),
                'scaled': event_data.get('grade', None) / event_data.get('max_grade', None)
                if event_data.get('max_grade', None) is not None and event_data.get('grade', None) is not None else None
            },
            response=event_data.get('answers', None)
        )
