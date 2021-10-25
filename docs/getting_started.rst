Introduction
===============

``event-routing-backends`` is developed as a pluggable application for the edx-platform. The code in this app hooks into the `event-tracking`_ app that is installed as a part of edx-platform. It provides new tracking backends and processors.

Features
--------

Events that need to be transformed can be filtered by their names using either `RegexFilter`_ processor or `NameWhitelist`_ processor offered by the ``event-tracking`` library. Both these processors run in the main thread. ``NameWhitelist`` performs simple string comparisons and is therefore, faster.

In ``event_tracking_backends``, two processors, namely `CaliperProcessor`_ and `XApiProcessor`_ can transform edX events into Caliper and xAPI format respectively. Events in Caliper format need to be passed through an additional processor named `CaliperEnvelopeProcessor`_, after being transformed and before being routed.

`EventsRouter`_ backend runs these processors and then routes the transformed events (xAPI or Caliper format) to configured routers. It is configured as a nested backend (named ``xapi`` or ``caliper``) of `AsyncRoutingBackend`_ (along with desired processors) in ``EVENT_TRACKING_BACKENDS`` configuration of the ``event-tracking`` library.

Execution
---------

``RegexFilter`` and ``NameWhitelist`` run synchronously in the main thread. Processors in ``xapi`` and ``caliper`` backends are executed asynchronously, with each backend executed as a separate celery task.

Routing of transformed events is also done asynchronously. Therefore, nested celery tasks are created, one for each configured router, to route events that have been transformed by ``xapi`` or ``caliper`` backends.

Retries
-------

Once an event fails to transmit due to connection error, it is retried periodically for a finite number of times, with delay between each retry. Total number of retries and delay (in seconds) between each retry can be configured using plugin setting ``EVENT_ROUTING_BACKEND_MAX_RETRIES`` (default: 3) and ``EVENT_ROUTING_BACKEND_COUNTDOWN`` (default: 30), respectively. If it still fails to transmit, then the event is dropped unless it is configured to persist in the database.

Persistence
-----------

Event consumers may never want to lose certain events even after a brief failure of the connection or at the endpoint. List of these events can be specified in plugin setting ``EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS``. Failed celery tasks for routing these events are persisted using `edx-celeryutils`_ package, once the retries have expired. ``edx-celeryutils`` also has `commands`_ for rerunning failed tasks and deleting old ones. Default list of events in ``EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS`` is:

#. ``edx.course.enrollment.activated``
#. ``edx.course.enrollment.deactivated``
#. ``edx.course.grade.passed.first_time``

Supported events
----------------

List of supported events can be found in `Supported_events <./event-mapping/Supported_events.rst>`_.


Mapping of edX event onto xAPI and Caliper formats
---------------------------------------------------

Mapping for xAPI events can be found in `xAPI mapping sheet <./event-mapping/xAPI_mapping.rst>`_.

Mapping for Caliper events can be found in `Caliper mapping google sheet <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_.

Version information of mapping
------------------------------

*Needs to be updated*

Installation
===============

Install event routing backends library or add it to private requirements of your virtual environment ( ``requirements/private.txt`` ).

#. Run ``pip install edx-event-routing-backends``.

#. Run migrations ( ``python manage.py lms migrate`` ).

#. Restart LMS service of edx-platform.

Configuration
===============

Two types of configuration are needed for the plugin:

#. Backends for filtering and transformation of selected events into ``xapi`` or ``caliper`` format.

#. Routers for routing transformed events to desired http endpoints.

Backends configuration
----------------------

By default, both ``caliper`` and ``xapi`` backends are configured with ``NameWhitelistProcessor`` that filters all the events currently supported. Users can override default backends to change filter type and name of the events to be filtered.

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

Router(s) for each backend can be configured in django admin settings as follows:

#. Navigate to http://localhost:18000/admin/event_routing_backends/routerconfiguration/add/

#. Select ``Backend name`` (``xapi`` or ``caliper``).

#. Add ``Route URL``; the HTTP endpoint where events are to be received.

#. Select ``Auth Scheme`` (``Basic`` or ``Bearer`` or ``None``). For ``Basic`` authentication, add ``username`` and ``password``. For ``Bearer`` authentication, add ``Token``.

#. Add ``Configurations`` comprising of following configuration items as json:

   #. ``override_args``: Accepts set of key:value pairs that will be added at the root level of the json of the event being routed. If the any of the keys already exist at the root level, their value will be overridden. Please note that for ``caliper`` backend, these changes will be made in the envelope.

   #. ``match_params``: This can be used to filter events based on values of keys in the original edX events. Regular expressions can be used for values.

   #. ``headers``: Additional headers can be specified here for ``caliper`` backend only.

A sample configuration for routing Caliper events having content organisation as ``edX`` AND course run is 2021 AND event name starts with ``problem`` OR event name contains ``video``, with override arguments and additional headers:

.. code-block:: JSON

   {
       "override_args":{
           "sensor_id":"sensor@example.com"
       },
       "headers":{
           "test":"header"
       },
       "match_params":{
           "course_id":"^.*course-v.:edX\\+.*\\+2021.*$",
           "name":[
               "^problem.*",
               "video"
           ]
       }
   }

A sample configuration for routing xAPI events if the enterprise is ``org_XYZ`` AND event name is ``edx.course.grade.passed.first_time`` OR ``edx.course.enrollment.activated``:

.. code-block:: JSON

   {
       "match_params":{
           "enterprise_uuid":"org_XYZ",
           "name":[
               "edx.course.grade.passed.first_time",
               "edx.course.enrollment.activated"
           ]
       }
   }

.. _event-tracking: https://github.com/edx/event-tracking

.. _NameWhitelist: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/whitelist.py

.. _RegexFilter: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

.. _save_statement: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/xapi_lrs_client.py#L70

.. _post: https://github.com/edx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/http_client.py#L67

.. _AsyncRoutingBackend: https://github.com/edx/event-tracking/blob/fccad3d118f594fe304ec48517e896447f15e782/eventtracking/backends/async_routing.py#L13

.. _CaliperProcessor: https://github.com/edx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/caliper/transformer_processor.py#L16

.. _XApiProcessor: https://github.com/edx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/xapi/transformer_processor.py#L16

.. _CaliperEnvelopeProcessor: https://github.com/edx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/caliper/envelope_processor.py#L12

.. _EventsRouter: https://github.com/edx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/backends/events_router.py#L15

.. _business_critical_events: https://github.com/edx/event-routing-backends/blob/e375674156b347be833ad8c2479be2c4ff4b073f/event_routing_backends/helpers.py#L197

.. _edx-celeryutils: https://github.com/edx/edx-celeryutils

.. _commands: https://github.com/edx/edx-celeryutils/tree/master/celery_utils/management/commands
