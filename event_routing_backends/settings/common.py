"""
Default settings for the event_routing_backends app.
"""


def plugin_settings(settings):
    """
    Adds default settings for the event_routing_backends app.
    """
    settings.CALIPER_EVENTS_ENABLED = False
    settings.CALIPER_EVENT_LOGGING_ENABLED = False
    settings.XAPI_EVENTS_ENABLED = True
    settings.XAPI_EVENT_LOGGING_ENABLED = True
    settings.EVENT_ROUTING_BACKEND_MAX_RETRIES = 3
    settings.EVENT_ROUTING_BACKEND_COUNTDOWN = 30
    settings.EVENT_ROUTING_BACKEND_BULK_DOWNLOAD_MAX_RETRIES = 3
    settings.EVENT_ROUTING_BACKEND_BULK_DOWNLOAD_COUNTDOWN = 1

    # .. setting_name: XAPI_AGENT_IFI_TYPE
    # .. setting_default: 'external_id'
    # .. setting_description: This setting can be used to specify the type of inverse functional identifier
    #    for actor in xAPI statements. Possible values are 'external_id', 'mbox_sha1sum' and 'mbox'
    #    when we set it to 'external_id' xAPI statement would represent actor like this
    #    ```
    #    {
    #        "objectType": "Agent",
    #        "account": {"homePage": "http://localhost:18000", "name": "32e08e30-f8ae-4ce2-94a8-c2bfe38a70cb"}
    #    }
    #    ```
    #    setting it to 'mbox' xAPI statement would represent actor like this
    #    ```
    #    {
    #        "objectType": "Agent",
    #        "mbox": "mailto:info@xapi.com"
    #    }
    #    ```
    #    setting it to 'mbox_sha1sum' xAPI statement would represent actor like this
    #    ```
    #    {
    #        "objectType": "Agent",
    #        mbox_sha1sum: "f427d80dc332a166bf5f160ec15f009ce7e68c4c"
    #    }
    #    ```
    settings.XAPI_AGENT_IFI_TYPE = 'external_id'

    # .. setting_name: EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS
    # .. setting_default: [
    #    'edx.course.enrollment.activated',
    #    'edx.course.enrollment.deactivated',
    #    'edx.course.grade.passed.first_time'
    #    ]
    # .. setting_description: This setting can be used to specify list of events which are
    #    treated as business critical events. For business critical events we persist them
    #    in case multiple attempts to rout them to relevant LRS are failed. Once persisted we can retry sending
    #    them once issues are resolved.
    settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS = [
        'edx.course.enrollment.activated',
        'edx.course.enrollment.deactivated',
        'edx.course.grade.passed.first_time'
    ]

    settings.EVENT_TRACKING_BACKENDS.update({
        'xapi': {
            'ENGINE': 'eventtracking.backends.async_routing.AsyncRoutingBackend',
            'OPTIONS': {
                'backend_name': 'xapi',
                'processors': [
                    {
                        'ENGINE': 'eventtracking.processors.whitelist.NameWhitelistProcessor',
                        'OPTIONS': {
                                'whitelist': [
                                    'edx.course.enrollment.activated',
                                    'edx.course.enrollment.deactivated',
                                    'edx.course.enrollment.mode_changed',
                                    'edx.grades.subsection.grade_calculated',
                                    'edx.grades.course.grade_calculated',
                                    'edx.special_exam.timed.attempt.created',
                                    'edx.special_exam.timed.attempt.submitted',
                                    'edx.special_exam.practice.attempt.created',
                                    'edx.special_exam.practice.attempt.submitted',
                                    'edx.special_exam.proctored.attempt.created',
                                    'edx.special_exam.proctored.attempt.submitted',
                                    'edx.completion.block_completion.changed',
                                    'edx.forum.thread.created',
                                    'edx.forum.thread.deleted',
                                    'edx.forum.thread.edited',
                                    'edx.forum.thread.viewed',
                                    'edx.forum.thread.reported',
                                    'edx.forum.thread.unreported',
                                    'edx.forum.thread.voted',
                                    'edx.forum.response.created',
                                    'edx.forum.response.deleted',
                                    'edx.forum.response.edited',
                                    'edx.forum.response.reported',
                                    'edx.forum.response.unreported',
                                    'edx.forum.response.voted',
                                    'edx.forum.comment.created',
                                    'edx.forum.comment.deleted',
                                    'edx.forum.comment.edited',
                                    'edx.forum.comment.reported',
                                    'edx.forum.comment.unreported',
                                    'edx.ui.lms.link_clicked',
                                    'edx.ui.lms.sequence.outline.selected',
                                    'edx.ui.lms.outline.selected',
                                    'edx.ui.lms.sequence.next_selected',
                                    'edx.ui.lms.sequence.previous_selected',
                                    'edx.ui.lms.sequence.tab_selected',
                                    'showanswer',
                                    'edx.problem.hint.demandhint_displayed',
                                    'problem_check',
                                    'load_video',
                                    'edx.video.loaded',
                                    'play_video',
                                    'edx.video.played',
                                    'complete_video',
                                    'edx.video.completed',
                                    'stop_video',
                                    'edx.video.stopped',
                                    'pause_video',
                                    'edx.video.paused',
                                    'seek_video',
                                    'edx.video.position.changed',
                                    'hide_transcript',
                                    'edx.video.transcript.hidden',
                                    'show_transcript',
                                    'edx.video.transcript.shown',
                                    'speed_change_video',
                                    'video_hide_cc_menu',
                                    'edx.video.closed_captions.shown',
                                    'edx.video.closed_captions.hidden',
                                    'edx.video.language_menu.hidden',
                                    'video_show_cc_menu',
                                    'edx.video.language_menu.shown',
                                    'edx.course.grade.passed.first_time'
                                ]
                        }
                    },
                ],
                'backends': {
                    'xapi': {
                        'ENGINE': 'event_routing_backends.backends.events_router.EventsRouter',
                        'OPTIONS': {
                            'processors': [
                                {
                                    'ENGINE':
                                        'event_routing_backends.processors.xapi.transformer_processor.XApiProcessor',
                                    'OPTIONS': {}
                                }
                            ],
                            'backend_name': 'xapi',
                        }
                    }
                },
            },
        },
        "caliper": {
            "ENGINE": "eventtracking.backends.async_routing.AsyncRoutingBackend",
            "OPTIONS": {
                "backend_name": "caliper",
                "processors": [
                    {
                        "ENGINE": "eventtracking.processors.whitelist.NameWhitelistProcessor",
                        "OPTIONS": {
                            "whitelist": [
                                'edx.course.enrollment.activated',
                                'edx.course.enrollment.deactivated',
                                'edx.ui.lms.link_clicked',
                                'edx.ui.lms.sequence.outline.selected',
                                'edx.ui.lms.outline.selected',
                                'edx.ui.lms.sequence.next_selected',
                                'edx.ui.lms.sequence.previous_selected',
                                'edx.ui.lms.sequence.tab_selected',
                                'showanswer',
                                'edx.problem.hint.demandhint_displayed',
                                'problem_check',
                                'load_video',
                                'edx.video.loaded',
                                'play_video',
                                'edx.video.played',
                                'complete_video',
                                'edx.video.completed',
                                'stop_video',
                                'edx.video.stopped',
                                'pause_video',
                                'edx.video.paused',
                                'seek_video',
                                'edx.video.position.changed',
                                'edx.course.grade.passed.first_time',
                                'edx.course.grade.now_passed',
                                'edx.course.grade.now_failed'
                            ]
                        }
                    }
                ],
                "backends": {
                    "caliper": {
                        "ENGINE": "event_routing_backends.backends.events_router.EventsRouter",
                        "OPTIONS": {
                            "processors": [
                                {
                                    "ENGINE":
                                        "event_routing_backends.processors."
                                        "caliper.transformer_processor.CaliperProcessor",
                                    "OPTIONS": {}
                                },
                                {
                                    "ENGINE":
                                        "event_routing_backends.processors."
                                        "caliper.envelope_processor.CaliperEnvelopeProcessor",
                                    "OPTIONS": {
                                        "sensor_id": settings.LMS_ROOT_URL
                                    }
                                }
                            ],
                            "backend_name": "caliper"
                        }
                    }
                }
            }
        }
    })
