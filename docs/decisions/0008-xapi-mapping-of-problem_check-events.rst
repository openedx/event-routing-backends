xAPI mapping of problem_check events
====================================

Status
------

Pending

Context
-------

#. Event named problem_check is emitted when:

   #. Learner submits solution to a problem. `event_source` is `browser` in this case.

   #. Server grades the submitted solution. `event_source` is `server` in this case.

#. Only the latter case in above, contains useful information such as grade, learner's answer etc.

#. xAPI specification provides a special schema for recording interaction with assessments. The specification assumes that each statement records interaction with only 1 assessment. However, lms studio allows grouping multiple assessments into a single assessment. And therefore, a single event is emitted even for a group of assessments.

#. Solution of an assessment (or group of assessments) can be found as a dictionary in `event.submission`.

#. Solution of each assessment in edX is defined by response type and input type defined in `event.submission.*.response_type` and `event.submission.*.input_type` respectively. The combination of `response_type` and `input_type` for each submission needs to be mapped with `interactionType` in xAPI specification.

#. Example of `submission` for a group of two assessments is as follows:

::

    "submission": {
             "389a51ad148a4a09bd9ae0f73482d2df_4_1":{
             "question": "What color is the sky?",
             "answer": "green",
             "response_type": "stringresponse",
             "input_type": "textline",
             "correct": false,
             "variant": "",
             "group_label": ""},

             "389a51ad148a4a09bd9ae0f73482d2df_5_1":{
             "question": "What is 5 times 3?",
             "answer": "15",
             "response_type": "numericalresponse",
             "input_type": "formulaequationinput",
             "correct": true,
             "variant": "",
             "group_label": ""}
         }


Decision
--------

1. Only the `problem_check` event having `event_source` as `server` will be transformed and emitted.

2. Mapping between `event.submission.*.response_type` and `event.submission.*.input_type` and `interactionType` is as follows:

.. list-table::
   :widths: 33 33 33
   :align: center
   :header-rows: 1

   * - response_type
     - input_type
     - interactionType
   * - stringresponse
     - textline
     - fill-in
   * - optionresponse
     - optioninput
     - choice
   * - choiceresponse
     - checkboxgroup
     - choice
   * - multiplechoiceresponse
     - choicegroup
     - choice
   * - numericalresponse
     - formulaequationinput
     - numeric
   * - All other combinations
     -
     - other

3. Learner's answers are mapped from `event.submission.*.answer` to `Result [response]`.

4. For an event containing multiple assessments:

   a. `interactionType` will be a list of strings, each representing an interaction type as per the table above.

   b. `Result [response]` will be a list of answers mapped from `event.submission.*.answer`.

5. xAPI spec does not specify that `interactionType` and `Result[response]` can be defined as lists. However, this is a better alternate to emitting multiple events for each assessment in a group of assessments, with same problem IDs.

6. Each key in `submission` where `key.response_type` is empty will be ignored.

7. xAPI spec allows for `correctResponsesPattern` to be emitted with each problem interaction event. This field will not be used because edX `problem_check` event does not contain information about correct answers.

8. xAPI spec allows for additional properties for certain event types like an array of choices for multiple choice assessments. These properties will not be used because `problem_check` event does not contain such information.
