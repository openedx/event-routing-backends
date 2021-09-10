Getting Started
===============

``event-routing-backends`` is developed as a pluggable application for the edx-platform. The code in this app hooks into the `event-tracking`_ app that is installed as a part of
edx-platform. It provides new tracking backends and processors.

.. _event-tracking: https://github.com/edx/event-tracking

Setup
------------
#. `event_tracking_backends` has two processors namely `CaliperProcessor` and `XApiProcessor` that can transform edX events into Caliper and xAPI format respectively. Events in Caliper format require an additional processor named `CaliperEnvelopeProcessor` before they can be routed.

#. Prior to being transformed into xAPI or Caliper format, edX events can be filtered by their names using either `RegexFilter`_ processor or `NameWhitelist`_ processor. Both of these processors run in the main thread and `NameWhitelist`_ is comparatively faster because it performs a simple string comparison.

#. We need to update ``EVENT_TRACKING_BACKENDS`` setting to create `xapi` and/or `caliper` backends with appropriate processors. Examples for creating each type of backend are presented below.

   #. A sample backend configuration for `caliper` is presented below. Here we are allowing only enrollment, `seek_video` and `edx.video.position.changed` events to be routed to `caliper` backend using `RegexFilter`_.

   .. code-block:: python

    EVENT_TRACKING_BACKENDS.update({
        'caliper': {
            'ENGINE': 'eventtracking.backends.async_routing.AsyncRoutingBackend',
            'OPTIONS': {
                'backend_name': 'caliper',
                'processors': [
                    {
                        'ENGINE': 'eventtracking.processors.regex_filter.RegexFilter',
                        'OPTIONS': {
                            'filter_type': 'allowlist',
                            'regular_expressions': [
                                'edx.course.enrollment.*',
                                'seek_video',
                                'edx.video.position.changed'
                            ]
                        }
                    }
                ],
                'backends': {
                    'caliper': {
                        'ENGINE': 'event_routing_backends.backends.events_router.EventsRouter',
                        'OPTIONS': {
                            'processors': [
                                {
                                    'ENGINE': 'event_routing_backends.processors.caliper.transformer_processor.CaliperProcessor',
                                    'OPTIONS': {}
                                },
                                {
                                    'ENGINE': 'event_routing_backends.processors.caliper.envelope_processor.CaliperEnvelopeProcessor',
                                    'OPTIONS': {
                                        'sensor_id': 'http://example.com/sensors'
                                    }
                                }
                            ],
                            'backend_name': 'caliper'
                        }
                    }
                }
            }
        }
    })

   #. A sample backend configuration for `xapi` is presented below. Here we are allowing only enrollment, `edx.course.grade.passed.first_time` and `edx.ui.lms.sequence.tab_selected` events to be routed to `xapi` backend using `NameWhitelist`_.

   .. code-block:: python

    EVENT_TRACKING_BACKENDS.update({
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
                                'edx.course.grade.passed.first_time',
                                'edx.ui.lms.sequence.tab_selected',
                            ]
                        }
                    }
                ],
                'backends': {
                    'xapi': {
                        'ENGINE': 'event_routing_backends.backends.events_router.EventsRouter',
                        'OPTIONS': {
                            'processors': [
                                {
                                    'ENGINE': 'event_routing_backends.processors.xapi.transformer_processor.XApiProcessor',
                                    'OPTIONS': {}
                                }
                            ],
                            'backend_name': 'xapi'
                        }
                    }
                }
            }
        }
    }

#. To add recipients for xAPI or Caliper events:

   #. log in to http://localhost:18000/admin/event_routing_backends/routerconfiguration/add/

   #. Add `Backend name` as `xapi` or `caliper` (same as the name of backend configured in `EVENT_TRACKING_BACKENDS`)

   #. Add `Route URL` where events are to be received.

   #. `Host configurations` requires following configuration items:

      #. `override_args`: Accepts set of key:value pairs that will be added at the root level of the json of the event being routed. If the any of the keys already exist at the root level, their values will be overridden.

      #. `router_type`: Two router types are available namely `XAPI_LRS` and `AUTH_HEADERS`. `XAPI_LRS` implements `save_statement`_ method of the `tincan` library and is ONLY to be used for routing xAPI events (i.e. `Backend name` = `xapi`). `AUTH_HEADERS` implements `post`_ method of the `requests` library and is ONLY to be used for routing Caliper events (i.e. `Backend name` = `caliper`).

      #. `host_configurations`: Authorization parameters are to be added here. Specify `username` and `password` for `Basic` http authentication. For other authentication types, specify `auth_key` and `auth_scheme`. Additional headers can be specified in value of `headers` key for `AUTH_HEADERS` router type ONLY.

      #. `match_params`: This can be used to filter events based on values of keys in the original edX events. Regular expressions can be used for values.

   #. A sample configuration for routing Caliper events having content organisation as `edX` AND course run is 2021 AND event name starts with `problem` OR event name contains `video`, using `Bearer` authentication, with override arguments and additional headers:

.. code-block:: JSON

    [
        {
            "override_args": {
                "sensor": "test.sensor.example.com",
            },
            "router_type": "AUTH_HEADERS",
            "host_configurations": {
                "auth_key": "token",
                "auth_scheme": "Bearer",
                "headers": {
                    "test": "header"
                }
            },
            "match_params": {
                "course_id": "^.*course-v.:edX\+.*\+2021.*$",
                "name": ["^problem.*", "video"]}
            }
        }
    ]

.

   #. A sample configuration for routing xAPI events if the enterprise is `org_XYZ` AND event name is `edx.course.grade.passed.first_time` OR `edx.course.enrollment.activated`, using `Basic` authentication:

.. code-block:: JSON

    [
        {
            "router_type":"XAPI_LRS",
            "host_configurations":{
                "username":"abc",
                "password":"pass",
            },
            "match_params": {
                "enterprise_uuid": "org_XYZ",
                "name": ["edx.course.grade.passed.first_time", "edx.course.enrollment.activated"]}
        }
    ]

#. After adding the `Host configurations` as per above, the setup is complete. Events should now begin routing to configured recipients.

.. _NameWhitelist: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/whitelist.py

.. _RegexFilter: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

.. _save_statement: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/xapi_lrs_client.py#L70

.. _post: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/http_client.py#L67


Local development
-----------------

If you have not already done so, create/activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/

Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements

Then you might want to run tests to make sure the setup went fine and there are no pre-existing problems (i.e. failed
tests or quality checks)

.. code-block:: bash

    $ make validate
