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

    "submission":{
            "389a51ad148a4a09bd9ae0f73482d2df_2_1":{
                "question":"Checkbox input here.",
                "answer":[
                    "an incorrect answer",
                    "a correct answer"
                ],
                "response_type":"choiceresponse",
                "input_type":"checkboxgroup",
                "correct":false,
                "variant":"",
                "group_label":""
            },
            "389a51ad148a4a09bd9ae0f73482d2df_6_1":{
                "question":"Drop down here.",
                "answer":"correct",
                "response_type":"optionresponse",
                "input_type":"optioninput",
                "correct":true,
                "variant":"",
                "group_label":""
            }
    }


Decision
--------

1. Only the `problem_check` event having `event_source` as `server` will be transformed and emitted.

2. Value of `interactionType` key in transformed event will be mapped based on `event.submission.*.response_type` and `event.submission.*.input_type` as listed in the table below:

.. list-table::
   :widths: 33 33 33
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

3. Learner's answers are mapped from `event.submission.*.answer` to `Result [response]` in the transformed event. !!!talk about lists!!!

4. For an event containing multiple assessments:

   a. Transformed event will be emitted with a single attachment.

   b. This attachment will be of type `application/json`.

   c. The attachment will contain keys `Objects` and `Results` with lists of `objects` and `results` as their values respectively.

   d. Each list entry of `objects` and `results` will contain information for a single submission.

::

    {
        'objects':[
            {
                'id':'block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df',
                'objectType':'Activity',
                'definition':{
                    'description':{
                        'en-US':'Checkbox input here.'
                    },
                    'type':'http://adlnet.gov/expapi/activities/cmi.interaction',
                    'interactionType':'choice'
                }
            },
            {
                'id':'block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df',
                'objectType':'Activity',
                'definition':{
                    'description':{
                        'en-US':'Drop down here.'
                    },
                    'type':'http://adlnet.gov/expapi/activities/cmi.interaction',
                    'interactionType':'choice'
                }
            },
        ],
        'results':[
            {
                'score':{
                    'scaled':0.4,
                    'raw':2.0,
                    'min':0.0,
                    'max':5.0
                },
                'success':False,
                'response':"['an incorrect answer', 'a correct answer']"
            },
            {
                'score':{
                    'scaled':0.4,
                    'raw':2.0,
                    'min':0.0,
                    'max':5.0
                },
                'success':False,
                'response':'correct'
            },
        ]
    }

6. Each key in `submission` where `key.response_type` is empty will be ignored.

7. xAPI spec allows for `correctResponsesPattern` to be emitted with each problem interaction event. This field will not be used because edX `problem_check` event does not contain information about correct answers.

8. xAPI spec allows for additional properties for certain event types like an array of choices for multiple choice assessments. These properties will not be used because `problem_check` event does not contain such information.
