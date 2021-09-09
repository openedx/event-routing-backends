Getting Started
===============

``event-routing-backends`` is developed as a pluggable application for the edx-platform. The code in this app hooks into the `event-tracking`_ app that is installed as a part of
edx-platform. It provides new tracking backends and processors.

.. _event-tracking: https://github.com/edx/event-tracking

Setup
------------

1. Navigate to `src` directory in `edx` repository.

2. Clone `event-routing-backends` and `event-tracking` (if not exists already).

   .. code-block:: bash

     $ git clone git@github.com:edx/event-tracking.git

     $ git clone git@github.com:edx/event-routing-backends.git

3. We need to update ``EVENT_TRACKING_BACKENDS`` setting to include backend configuration. To do that, create a file named `private.py` in `edx-platform/lms/envs` and in `edx-platform/cms/envs`. Add configuration for `xapi` and `caliper` backend in `private.py` as shown below.

   a. Prior to being transformed into xAPI or Caliper format, edX events can be filtered with either a `RegexFilter`_ or `NameWhitelist`_. Both of these filters run in the main thread and `NameWhitelist`_ is comparatively faster because it performs a simple string comparison. Examples of both filter types are covered in example configurations of `xapi` and `caliper` backends below.

   b. A sample configuration for `private.py` is presented below. Here we are allowing only enrollment, seek_video and edx.video.position.changed events to be routed to `caliper` backend using `RegexFilter`_.

   .. code-block:: python

    from .common import EVENT_TRACKING_BACKENDS
    CALIPER_EVENTS_ENABLED = True
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

   b. A sample configuration for `private.py` is presented below. Here we are allowing only enrollment, `edx.course.grade.passed.first_time` and `edx.ui.lms.sequence.tab_selected` events to be routed to `xapi` backend using `NameWhitelist`_.

   .. code-block:: python

    from .common import EVENT_TRACKING_BACKENDS
    XAPI_EVENTS_ENABLED = True
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

4. Navigate to `devstack` directory in `edx` repository.

5. Start app containers (if not up already).

   .. code-block:: bash

    $ make dev.up.large-and-slow

6. Start lms shell

   .. code-block:: bash

    $ make lms-shell

7. Install `event-routing-backends` and `event-tracking` (if not installed already).

   .. code-block:: bash

    pip install -e /edx/src/event-tracking/
    pip install -e /edx/src/event-routing-backends/

8. Install dependencies.

   .. code-block:: bash

    make requirements

9. Make and perform migrations

   .. code-block:: bash

    python manage.py lms makemigrations

    python manage.py lms migrate

10. To add recipients for xAPI or Caliper events, log in to http://localhost:18000/admin/event_routing_backends/routerconfiguration/add/.

11. Add `Backend name` as `xapi` or `caliper`.

12. Add `Route URL` where events are to be received.

13. `Host configurations` requires following configuration items:

   a. `override_args`: Accepts set of key:value pairs that will be added at the root level of the json of the event being routed. If the any of the keys already exist at the root level, their values will be overridden.

   b. `router_type`: Two router types are available namely `XAPI_LRS` and `AUTH_HEADERS`. `XAPI_LRS` implements `save_statement`_ method of the `tincan` library and is ONLY to be used for routing xAPI events (i.e. `Backend name` = `xapi`). `AUTH_HEADERS` implements `post`_ method of the `requests` library and is ONLY to be used for routing Caliper events (i.e. `Backend name` = `caliper`).

   c. `host_configurations`: Authorization parameters are to be added here. Specify `username` and `password` for `Basic` http authentication. For other authentication types, specify `auth_key` and `auth_scheme`. Additional headers can be specified in value of `headers` key for `AUTH_HEADERS` router type ONLY.

   d. `match_params`: This can be used to filter events based on values of keys in the original edX events. Regular expressions can be used for values.

   e. Examples of `Host configurations` are:

      i. A sample configuration for routing Caliper events having content organisation as `edX` AND course run is 2021 AND event name starts with `problem` OR event name contains `video`, using `Bearer` authentication, with override arguments and additional headers:

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

      ii. A sample configuration for routing xAPI events if the enterprise is `org_XYZ` AND event name is `edx.course.grade.passed.first_time` OR `edx.course.enrollment.activated`, using `Basic` authentication:

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

14. After adding the `Host configurations` as per above, the setup is complete. Events should now begin routing to configured recipients.

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
