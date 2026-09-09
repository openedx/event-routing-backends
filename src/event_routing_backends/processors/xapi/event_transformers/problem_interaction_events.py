"""
Transformers for problem interaction events.
"""
import json

from tincan import Activity, ActivityDefinition, Extensions, LanguageMap, Result

from event_routing_backends.helpers import get_problem_block_id
from event_routing_backends.processors.openedx_filters.decorators import openedx_filter
from event_routing_backends.processors.xapi import constants
from event_routing_backends.processors.xapi.registry import XApiTransformersRegistry
from event_routing_backends.processors.xapi.statements import GroupActivity
from event_routing_backends.processors.xapi.transformer import (
    OneToManyChildXApiTransformerMixin,
    OneToManyXApiTransformerMixin,
    XApiTransformer,
    XApiVerbTransformerMixin,
)

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

    @openedx_filter(
        filter_type="event_routing_backends.processors.xapi.problem_interaction_events.base_problems.get_object",
    )
    def get_object(self):
        """
        Get object for xAPI transformed event.
        Returns:
            `Activity`
        """
        object_id = self.get_object_id()
        definition = self.get_object_definition()
        return Activity(
            id=object_id,
            definition=definition,
        )

    def get_object_id(self):
        """
        Returns the object.id

        Returns:
            str
        """
        object_id = None
        data = self.get_data('data')
        if data and isinstance(data, dict):
            object_id = self.get_data('data.problem_id') or self.get_data('data.module_id', True)
        else:
            object_id = self.get_data('usage_key')

        return object_id

    def get_object_definition(self):
        """
        Returns the definition portion of the object stanza.

        Returns:
            ActivityDefinition
        """
        event_name = self.get_data('name', True)

        return ActivityDefinition(
            type=EVENT_OBJECT_DEFINITION_TYPE[event_name] if event_name in EVENT_OBJECT_DEFINITION_TYPE else
            constants.XAPI_ACTIVITY_INTERACTION,
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


class BaseProblemCheckTransformer(BaseProblemsTransformer):
    """
    Transform problem check events into one or more xAPI statements.

    If there is only one question in the source event problem, then transform() returns a single Activity.

    But if there are multiple questions in the source event problem, transform() will return:

    * 1 parent GroupActivity
    * N "child" Activity which reference the parent, where N>=0
    """
    additional_fields = ('result', )

    @openedx_filter(
        filter_type="event_routing_backends.processors.xapi.problem_interaction_events.base_problem_check.get_object",
    )
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

        return xapi_object

    def get_object_definition(self):
        """
        Returns the definition portion of the object stanza.

        Returns:
            ActivityDefinition
        """
        definition = super().get_object_definition()

        if self.get_data('data.attempts'):
            definition.extensions = Extensions({
                constants.XAPI_ACTIVITY_ATTEMPT: self.get_data('data.attempts')
            })
        interaction_type = self._get_interaction_type()
        display_name = self.get_data('display_name')
        submission = self._get_submission()
        if submission:
            interaction_type = INTERACTION_TYPES_MAP.get(submission.get('response_type'), DEFAULT_INTERACTION_TYPE)
            definition.description = LanguageMap({constants.EN_US: submission['question']})
        elif display_name:
            definition.name = LanguageMap({constants.EN_US: display_name})

        definition.interaction_type = interaction_type

        return definition

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
            correct = submission.get("correct")
        else:
            # The submission key didn't exist until March 2014, prior to that
            # there was usually a version of the answer in the "answers" key,
            # but it is very flaky (sometimes containing xml, and without the
            # appended variant identifier that we get for free in the
            # submission. We don't attempt to work around those issues here due
            # to how few and how old those events are and how complicated the
            # parsing is. Should we ever find it necessary to make a better
            # parser for them, Insights had a good effort here:
            # https://github.com/openedx/edx-analytics-pipeline/blob/8d96f93/edx/analytics/tasks/insights/answer_dist.py#L260C36-L260C36
            response = event_data.get('answers', None)
            correct = self.get_data('success') == 'correct'

        max_grade = self.get_data('max_grade')
        grade = self.get_data('grade')
        scaled = None

        if max_grade is not None and grade is not None:
            if max_grade > 0:
                scaled = grade / max_grade
            else:
                scaled = 0

        # Some problems can provide a list of responses answers, but
        # the Result type wants a string for "response". So we dump those
        # to JSON here to provide a parsable version of the response instead
        # of getting the __repr__ of the list, which is what Result will
        # generate by default.
        if isinstance(response, list):
            cls = JSONEncodedResult
        else:
            cls = Result

        return cls(
            success=correct,
            score={
                'min': 0,
                'max': max_grade,
                'raw': grade,
                'scaled': scaled,
            },
            response=response
        )


@XApiTransformersRegistry.register('problem_check')
class ProblemCheckTransformer(OneToManyXApiTransformerMixin, BaseProblemCheckTransformer):
    """
    Transform problem check events into one or more xAPI statements.

    If there is only one question in the source event problem, then transform() returns a single Activity.

    But if there are multiple questions in the source event problem, transform() will return:

    * 1 parent GroupActivity
    * N "child" Activity which reference the parent, where N>=0
    """
    @property
    def child_transformer_class(self):
        """
        Returns the ProblemCheckChildTransformer class.

        Returns:
            Type
        """
        return ProblemCheckChildTransformer

    def get_child_ids(self):
        """
        Returns the list of "child" event IDs.

        In this context, "child" events relate to multiple submissions to sub-questions in the problem.

        If <1 children are found on this event, then <1 child events are returned in the list.
        Otherwise, we say that "this event has no children", and so this method returns an empty list.

        Returns:
            list of strings
        """
        submissions = self.get_data('submission') or {}
        child_ids = submissions.keys()
        if len(child_ids) > 1:
            return child_ids
        return []

    def get_object(self):
        """
        Get object for xAPI transformed event or group of events.

        Returns:
            `Activity` or `GroupActivity`
        """
        activity = super().get_object()
        definition = self.get_object_definition()

        if self.get_child_ids():
            activity = GroupActivity(
                id=activity.id,
                definition=definition,
            )

        return activity

    def get_object_definition(self):
        """
        Returns the definition portion of the object stanza.

        Returns:
            ActivityDefinition
        """
        definition = super().get_object_definition()

        if self.get_child_ids():
            definition.interaction_type = DEFAULT_INTERACTION_TYPE

        return definition


class ProblemCheckChildTransformer(OneToManyChildXApiTransformerMixin, BaseProblemCheckTransformer):
    """
    Transformer for subproblems of a multi-question problem_check event.
    """
    def _get_submission(self):
        """
        Return this child's submission data from the event data, if valid.

        Returns:
            dict
        """
        submissions = self.get_data('submission') or {}
        return submissions.get(self.child_id)

    def get_object_id(self):
        """
        Returns the child object.id, which it creates from the parent object.id
        and the child_id.

        Returns:
            str
        """
        object_id = super().get_object_id() or ""
        object_id = '@'.join([
            *object_id.split('@')[:-1],
            self.child_id,
        ])
        return object_id

    def get_result(self):
        """
        Get result for the xAPI transformed child event.

        Returns:
            `Result`
        """
        result = super().get_result()
        # Don't report the score on child events; only the parent knows the score.
        result.score = None
        submission = self._get_submission() or {}
        result.response = submission.get('answer')
        return result


class JSONEncodedResult(Result):
    """
    This is a workaround for a TinCan issue where it will coerce a value passed
    in for a `response` to str. This breaks our ability to serialize list
    responses into JSON, so we override it here.
    """
    @property
    def response(self):
        """Response for Result

        :setter: Tries to JSON dump the list value.
        :setter type: list
        :rtype: str
        """
        return self._response

    @response.setter
    def response(self, value):
        """
        Ensures the list is serialized as JSON.
        """
        if not isinstance(value, list):
            raise ValueError(f"JSONEncodedResult only accepts lists, {type(value)} given.")

        self._response = json.dumps(value, ensure_ascii=False)
