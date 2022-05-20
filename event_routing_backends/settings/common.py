"""
Default settings for the event_routing_backends app.
"""


def plugin_settings(settings):
    """
    Adds default settings for the event_routing_backends app.
    """
    settings.CALIPER_EVENTS_ENABLED = False
    settings.XAPI_EVENTS_ENABLED = True
    settings.EVENT_ROUTING_BACKEND_MAX_RETRIES = 3
    settings.EVENT_ROUTING_BACKEND_COUNTDOWN = 30

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
