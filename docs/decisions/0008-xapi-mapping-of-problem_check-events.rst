xAPI mapping of problem_check events
====================================

Status
------

Pending

Context
-------

#. Event named `problem_check` is emitted when:

   #. Learner submits solution to a problem. `event_source` is `browser` in this case.

   #. Server grades the submitted solution. `event_source` is `server` in this case.

#. Only the latter in above, contains useful information such as grade, learner's answer etc.

#. Solution of an assessment (or group of assessments) can be found in `data.submission`.

#. Each solution in `data.submission` is defined by response type and input type defined in `data.submission.*.response_type` and `data.submission.*.input_type` respectively. The combination of `response_type` and `input_type` for each submission needs to be mapped with `interactionType` in xAPI specification.

#. xAPI specification provides a special schema for recording interaction with assessments. The specification assumes that each statement records interaction with only one assessment. However, edX studio allows grouping multiple assessments into a single assessment. And therefore, a single `problem_check` event is emitted even for a group of assessments as seen in `Appendix A`_.

#. In case of `problem_check` event having multiple submissions in `event.submission`, one of the following approach needs to be implemented:

   #. Multiple xAPI transformed events can be emitted, each containing information regarding one of the submissions. Grades of the problem (`data.grade` and `data.max_grade`) will then have to be calculated for each submission based on the value of `data.submission.*.correct`.

   #. A single xAPI transformed event can be emitted having information mapped from any one of the submissions. Information about the rest of the submissions can be emitted in an attachment with this event.

Decision
--------

1. Only the `problem_check` event having `event_source` as `server` will be transformed and emitted.

2. Value of `interactionType` key in transformed event will be mapped based on `data.submission.*.response_type` and `data.submission.*.input_type` as listed in the table below:

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

3. Learner's answers are mapped from `data.submission.*.answer` to `Result [response]` in the transformed event. As per specification, `Result [response]` needs to be a string. Therefore any lists in `data.submission.*.answer` will be converted to a string delimited by pipe character (`|`).

4. Each key in `submission` where `key.response_type` is empty will be ignored.

5. xAPI spec allows for `correctResponsesPattern` to be emitted with each problem interaction event. This field will not be used because edX `problem_check` event does not contain information about correct answers.

6. xAPI spec allows for additional properties for certain event types like an array of choices for multiple choice assessments. These properties will not be used because `problem_check` event does not contain such information.

7. For an event containing multiple assessments:

   a. The approach involving multiple transformed events will not be used because:

      i. This approach would have required manipulating the grading of problems already graded by the server.

      ii. It would have required significant changes in workflow of `event-routing-backends` application. At present, the application generates only one transformed version for a given event.

   b. Instead, the transformed event will be emitted with a single attachment.

   c. This attachment will be of type `application/json`.

   d. The attachment will contain keys `Objects` and `Results` with lists of `objects` and `results` as their values respectively.

   e. Each list entry of `objects` and `results` will contain information for a single submission.

8. Example of header and body of a post request for a `problem_check` event in `Appendix A`_ is presented in `Appendix B`_.


.. _Appendix A:

Appendix A
----------
::

    {
        "name":"problem_check",
        "timestamp":"2021-07-28T06:39:07.422913+00:00",
        "data":{
            "state":{
                "seed":1,
                "student_answers":{
                    "389a51ad148a4a09bd9ae0f73482d2df_6_1":"correct",
                    "389a51ad148a4a09bd9ae0f73482d2df_4_1":"answer",
                    "389a51ad148a4a09bd9ae0f73482d2df_2_1":[
                        "choice_0",
                        "choice_3"
                    ],
                    "389a51ad148a4a09bd9ae0f73482d2df_5_1":"100",
                    "389a51ad148a4a09bd9ae0f73482d2df_3_1":"choice_2"
                },
                "has_saved_answers":false,
                "correct_map":{
                    "389a51ad148a4a09bd9ae0f73482d2df_2_1":{
                        "correctness":"correct",
                        "npoints":null,
                        "msg":"",
                        "hint":"",
                        "hintmode":null,
                        "queuestate":null,
                        "answervariable":null
                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_3_1":{
                        "correctness":"correct",
                        "npoints":null,
                        "msg":"",
                        "hint":"",
                        "hintmode":null,
                        "queuestate":null,
                        "answervariable":null
                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_4_1":{
                        "correctness":"correct",
                        "npoints":null,
                        "msg":"",
                        "hint":"",
                        "hintmode":null,
                        "queuestate":null,
                        "answervariable":null
                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_5_1":{
                        "correctness":"correct",
                        "npoints":null,
                        "msg":"",
                        "hint":"",
                        "hintmode":null,
                        "queuestate":null,
                        "answervariable":null
                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_6_1":{
                        "correctness":"correct",
                        "npoints":null,
                        "msg":"",
                        "hint":"",
                        "hintmode":null,
                        "queuestate":null,
                        "answervariable":null
                    }
                },
                "input_state":{
                    "389a51ad148a4a09bd9ae0f73482d2df_2_1":{

                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_3_1":{

                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_4_1":{

                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_5_1":{

                    },
                    "389a51ad148a4a09bd9ae0f73482d2df_6_1":{

                    }
                },
                "done":true
            },
            "problem_id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
            "answers":{
                "389a51ad148a4a09bd9ae0f73482d2df_2_1":[
                    "choice_2",
                    "choice_3"
                ],
                "389a51ad148a4a09bd9ae0f73482d2df_6_1":"correct",
                "389a51ad148a4a09bd9ae0f73482d2df_4_1":"not an answer",
                "389a51ad148a4a09bd9ae0f73482d2df_3_1":"choice_1",
                "389a51ad148a4a09bd9ae0f73482d2df_5_1":"100"
            },
            "grade":2,
            "max_grade":5,
            "correct_map":{
                "389a51ad148a4a09bd9ae0f73482d2df_2_1":{
                    "correctness":"incorrect",
                    "npoints":null,
                    "msg":"",
                    "hint":"",
                    "hintmode":null,
                    "queuestate":null,
                    "answervariable":null
                },
                "389a51ad148a4a09bd9ae0f73482d2df_3_1":{
                    "correctness":"incorrect",
                    "npoints":null,
                    "msg":"",
                    "hint":"",
                    "hintmode":null,
                    "queuestate":null,
                    "answervariable":null
                },
                "389a51ad148a4a09bd9ae0f73482d2df_4_1":{
                    "correctness":"incorrect",
                    "npoints":null,
                    "msg":"",
                    "hint":"",
                    "hintmode":null,
                    "queuestate":null,
                    "answervariable":null
                },
                "389a51ad148a4a09bd9ae0f73482d2df_5_1":{
                    "correctness":"correct",
                    "npoints":null,
                    "msg":"",
                    "hint":"",
                    "hintmode":null,
                    "queuestate":null,
                    "answervariable":null
                },
                "389a51ad148a4a09bd9ae0f73482d2df_6_1":{
                    "correctness":"correct",
                    "npoints":null,
                    "msg":"",
                    "hint":"",
                    "hintmode":null,
                    "queuestate":null,
                    "answervariable":null
                }
            },
            "success":"incorrect",
            "attempts":3,
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
                },
                "389a51ad148a4a09bd9ae0f73482d2df_4_1":{
                    "question":"Text input here (\"answer\").",
                    "answer":"not an answer",
                    "response_type":"stringresponse",
                    "input_type":"textline",
                    "correct":false,
                    "variant":"",
                    "group_label":""
                },
                "389a51ad148a4a09bd9ae0f73482d2df_3_1":{
                    "question":"Multiple choice input here.",
                    "answer":"incorrect",
                    "response_type":"multiplechoiceresponse",
                    "input_type":"choicegroup",
                    "correct":false,
                    "variant":"",
                    "group_label":""
                },
                "389a51ad148a4a09bd9ae0f73482d2df_5_1":{
                    "question":"Numerical input here (100).",
                    "answer":"100",
                    "response_type":"numericalresponse",
                    "input_type":"formulaequationinput",
                    "correct":true,
                    "variant":"",
                    "group_label":""
                }
            }
        },
        "context":{
            "course_id":"course-v1:edX+DemoX+Demo_Course",
            "course_user_tags":{

            },
            "session":"dc4d4862f54a6d3de1d203d5e063d1f2",
            "user_id":7,
            "username":"verified",
            "ip":"172.18.0.1",
            "host":"localhost:18000",
            "agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "path":"/courses/course-v1:edX+DemoX+Demo_Course/xblock/block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df/handler/xmodule_handler/problem_check",
            "referer":"http://localhost:18000/xblock/block-v1:edX+DemoX+Demo_Course+type@vertical+block@2fceba7d458447f380da0959e82d8d92?show_title=0&show_bookmark_button=0&recheck_access=1&view=student_view",
            "accept_language":"en-GB,en-US;q=0.9,en;q=0.8",
            "client_id":null,
            "org_id":"edX",
            "module":{
                "display_name":"Multiple questions",
                "usage_key":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df"
            },
            "asides":{

            },
            "event_source":"server",
            "page":"x_module"
        }
    }

.. _Appendix B:

Appendix B
----------

**Header of post request:**

::

   {
    'User-Agent':'python-requests/2.26.0',
    'Accept-Encoding':'gzip, deflate',
    'Accept':'*/*',
    'Connection':'keep-alive',
    'X-Experience-API-Version':'1.0.1',
    'Content-Type':"multipart/mixed; boundary=abcABC0123'()+_,-./:=?",
    'Content-Length':'3581',
    'Authorization':'Basic bkZLdnVQWjhvZDlVSGpSZmV6ZzpvOEJwbzVOa1NHdllvUmNUY3g4'
   }

**Body of post request:**

::

    --abcABC0123'()+_,-./:=?
    Content-Disposition: form-data; name="randomField1"; filename="randomFilename1"
    Content-Type: application/json

    {
        "result":{
            "score":{
                "scaled":0.4,
                "raw":2.0,
                "min":0.0,
                "max":5.0
            },
            "success":false,
            "response":"100"
        },
        "version":"1.0.3",
        "actor":{
            "objectType":"Agent",
            "openid":"https://openedx.org/users/user-v1/32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb"
        },
        "verb":{
            "id":"http://adlnet.gov/expapi/verbs/answered",
            "display":{
                "en-US":"answered"
            }
        },
        "object":{
            "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
            "objectType":"Activity",
            "definition":{
                "description":{
                    "en-US":"Numerical input here (100)."
                },
                "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                "interactionType":"numeric"
            }
        },
        "context":{
            "contextActivities":{
                "parent":[
                    {
                        "id":"course-v1:edX+DemoX+Demo_Course",
                        "objectType":"Activity"
                    }
                ]
            }
        },
        "attachments":[
            {
                "usageType":"http://id.tincanapi.com/attachment/supporting_media",
                "display":{
                    "en-US":"supporting media"
                },
                "contentType":"application/json",
                "length":2001,
                "sha2":"1efeee7dd1170cfd7d31f4b50b489cc9182ff874a0744dcc05c58ea4392158ae",
                "description":{
                    "en-US":"A media file that supports the experience. For example a video that shows the experience taking place"
                }
            }
        ]
    }
    --abcABC0123'()+_,-./:=?
    Content-Disposition: form-data; name="randomField2"; filename="randomFilename2"
    Content-Type: application/json
    Content-Transfer-Encoding: binary
    X-Experience-API-Hash: 1efeee7dd1170cfd7d31f4b50b489cc9182ff874a0744dcc05c58ea4392158ae

    {
        "objects":[
            {
                "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
                "objectType":"Activity",
                "definition":{
                    "description":{
                        "en-US":"Checkbox input here."
                    },
                    "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                    "interactionType":"choice"
                }
            },
            {
                "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
                "objectType":"Activity",
                "definition":{
                    "description":{
                        "en-US":"Drop down here."
                    },
                    "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                    "interactionType":"choice"
                }
            },
            {
                "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
                "objectType":"Activity",
                "definition":{
                    "description":{
                        "en-US":"Text input here (\"answer\")."
                    },
                    "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                    "interactionType":"fill-in"
                }
            },
            {
                "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
                "objectType":"Activity",
                "definition":{
                    "description":{
                        "en-US":"Multiple choice input here."
                    },
                    "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                    "interactionType":"choice"
                }
            },
            {
                "id":"block-v1:edX+DemoX+Demo_Course+type@problem+block@389a51ad148a4a09bd9ae0f73482d2df",
                "objectType":"Activity",
                "definition":{
                    "description":{
                        "en-US":"Numerical input here (100)."
                    },
                    "type":"http://adlnet.gov/expapi/activities/cmi.interaction",
                    "interactionType":"numeric"
                }
            }
        ],
        "results":[
            {
                "score":{
                    "scaled":0.4,
                    "raw":2.0,
                    "min":0.0,
                    "max":5.0
                },
                "success":false,
                "response":"['an incorrect answer', 'a correct answer']"
            },
            {
                "score":{
                    "scaled":0.4,
                    "raw":2.0,
                    "min":0.0,
                    "max":5.0
                },
                "success":false,
                "response":"correct"
            },
            {
                "score":{
                    "scaled":0.4,
                    "raw":2.0,
                    "min":0.0,
                    "max":5.0
                },
                "success":false,
                "response":"not an answer"
            },
            {
                "score":{
                    "scaled":0.4,
                    "raw":2.0,
                    "min":0.0,
                    "max":5.0
                },
                "success":false,
                "response":"incorrect"
            },
            {
                "score":{
                    "scaled":0.4,
                    "raw":2.0,
                    "min":0.0,
                    "max":5.0
                },
                "success":false,
                "response":"100"
            }
        ]
    }
    --abcABC0123'()+_,-./:=?--
