Introduction
===============

``event-routing-backends`` is developed as a pluggable application for the edx-platform. The code in this app hooks into the `event-tracking`_ app that is installed as a part of
edx-platform. It provides new tracking backends and processors.

Features
--------

Events that need to be transformed can be filtered by their names using either `RegexFilter`_ processor or `NameWhitelist`_ processor offered by the ``event-tracking`` library. Both these processors run in the main thread. ``NameWhitelist`` performs simple string comparisons and is therefore, faster.

Two processors, namely ``CaliperProcessor`` and ``XApiProcessor``, in ``event_tracking_backends`` can transform edX events into Caliper and xAPI format respectively. Events in Caliper format need to be passed through an additional processor named `CaliperEnvelopeProcessor`, after being transformed and before being routed.

``EventsRouter`` processor in ``event_tracking_backends``, can route the transformed events (xAPI and Caliper format) to configured routers.

The processors discussed above, are configured as nested backends (named ``xapi`` or ``caliper``) of `AsyncRoutingBackend`_ in ``EVENT_TRACKING_BACKENDS`` configuration of ``event-tracking`` library.

Execution
---------

``RegexFilter`` and ``NameWhitelist`` run synchronously in the main thread. Processors in ``xapi`` and ``caliper`` backends are executed asynchronously, with each backend run as a separate celery task.

Routing of transformed events is also done asynchronously. Therefore, nested celery tasks are created, one for each router, to route events that have been transformed by ``xapi`` or ``caliper`` backends.

Retries
-------

Once an event fails to transmit due to connection error, it is retried after a delay of 30 seconds for 3 more times. If it still fails to transmit, then event is dropped unless it is configured to persist in the datebase.

Persistence
-----------

Some events are critical for record keeping and should never be lost. These `business_critical_events`_ are persisted in the database even after the retries expire. Retry is attempted to transmit persisted events once a day. Following events are configured as ``business_critical_events``:

#. ``edx.course.enrollment.activated``
#. ``edx.course.enrollment.deactivated``
#. ``edx.course.grade.passed.first_time``

.. _business_critical_events: https://github.com/edx/event-routing-backends/blob/e375674156b347be833ad8c2479be2c4ff4b073f/event_routing_backends/helpers.py#L197

Supported events
----------------

List of supported events can be found here :any:`supported-events`.


Mapping of edX event onto xAPI and Caliper formats
---------------------------------------------------

Mapping for Caliper events can be found `Caliper mapping <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_.

Mapping for xAPI events can be found in `xAPI mapping <https://docs.google.com/spreadsheets/d/1hvOvJnWD9d00QjPoou0wTxx5gTsqk5uda6RJp56LJjI/edit?usp=sharing>`_.

Version information of mapping
------------------------------

*Needs to be updated*

Installation
===============
#. Upgrade edX devstack to latest master branch.

#. Start devstack and ssh into ``lms`` docker container (``make lms-shell``).

#. Run ``pip install edx-event-routing-backends``.

#. Run migrations (``python manage.py lms migrate``).

#. Exit shell (``exit``) and restart lms container (``make lms-stop`` and ``make lms-up``).

Configuration
===============

Two types of configuration are needed for the plugin:

#. Backends for transformation of selected events into ``xapi`` or ``caliper`` format.

#. Routers for routing transformed events to desired http endpoints.

Backends configuration
----------------------

By default, both `caliper` and `xapi` backends are configured with ``NameWhitelistProcessor`` that filters all the events currently supported. Users can override default backends to change filter type and name of the events to be filtered.


A sample override for ``caliper`` backend is presented below. Here we are allowing only enrollment, ``seek_video`` and ``edx.video.position.changed`` events to be filtered through `RegexFilter`_ to ``caliper`` backend.

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

A sample override for ``xapi`` backend is presented below. Here we are allowing only enrollment, ``edx.course.grade.passed.first_time`` and ``edx.ui.lms.sequence.tab_selected`` events to be filtered through `NameWhitelist`_ to ``xapi`` backend.

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

Router configuration
--------------------

Routers can be configured in django admin settings and require following properties:

#. ``Backend name``: `xapi` or `caliper` (same as the name of backend configured in ``EVENT_TRACKING_BACKENDS`` explained above).

#. ``Route URL``: The HTTP endpoint where events are to be received.

#. ``Host configurations``: Comprising of following configuration items:

   #. ``override_args``: Accepts set of key:value pairs that will be added at the root level of the json of the event being routed. If the any of the keys already exist at the root level, their value will be overridden.

   #. ``router_type``: Two router types are available namely ``XAPI_LRS`` and ``AUTH_HEADERS``. ``XAPI_LRS`` implements `save_statement`_ method of the ``tincan`` library and is ONLY to be used for routing xAPI events (i.e. ``Backend name`` as ``xapi``). `AUTH_HEADERS` implements `post`_ method of the ``requests`` python library and is ONLY to be used for routing Caliper events (i.e. ``Backend name`` as ``caliper``).

   #. ``host_configurations``: Authorisation parameters are to be added here. Specify ``username`` and ``password`` for ``Basic`` http authentication. For other authentication types, specify ``auth_key`` and ``auth_scheme`` (instead of ``username`` and ``password``). Additional headers can be specified in value of ``headers`` key for ``AUTH_HEADERS`` router type ONLY.

   #. ``match_params``: This can be used to filter events based on values of keys in the original edX events. Regular expressions can be used for values.

A sample configuration for routing Caliper events having content organisation as ``edX`` AND course run is 2021 AND event name starts with ``problem`` OR event name contains ``video``, using ``Bearer`` authentication, with override arguments and additional headers:

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
    ]

A sample configuration for routing xAPI events if the enterprise is ``org_XYZ`` AND event name is ``edx.course.grade.passed.first_time`` OR ``edx.course.enrollment.activated``, using ``Basic`` authentication:

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

To configure routers for routing the transformed events:

#. Log in to http://localhost:18000/admin/event_routing_backends/routerconfiguration/add/

#. Add ``Backend name`` as ``xapi`` or ``caliper`` (same as the name of backend configured in `EVENT_TRACKING_BACKENDS` setting)

#. Add ``Route URL`` where events are to be received.

#. Add ``Host configurations`` as described above.

Events (transformed by configured ``Backend name``) should now begin routing to configured ``Route URL``. More than one router configurations can be added for a backend.

.. _event-tracking: https://github.com/edx/event-tracking

.. _NameWhitelist: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/whitelist.py

.. _RegexFilter: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

.. _save_statement: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/xapi_lrs_client.py#L70

.. _post: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/http_client.py#L67

.. _AsyncRoutingBackend: https://github.com/edx/event-tracking/blob/fccad3d118f594fe304ec48517e896447f15e782/eventtracking/backends/async_routing.py#L13

.
