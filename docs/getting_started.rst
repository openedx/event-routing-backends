
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

Supported events and mapping of edx events onto xAPI and Caliper formats
------------------------------------------------------------------------

List of supported edx events can be found in `Supported_events <https://github.com/openedx/event-routing-backends/blob/master/docs/event-mapping/Supported_events.rst>`_ along with their mapping onto xAPI and Caliper format.

Version information of transformer
----------------------------------

Version of transformer is semantic version of event-routing-backend prefixed with  `event-routing-backends@` included in the statement/event. Version is a string of format "event-routing-backend@X.Y.Z" where increment in X represents breaking changes and increment in Y represents addition/update of fields in the event/statement and Z represents bug fix or patched version.

In xAPI statement, version is in value of the key ``https://w3id.org/xapi/openedx/extension/transformer-version`` in ``extensions`` of ``Context`` of the statement.

In Caliper event, version is in value of the key ``transformerVersion`` in ``extensions`` of the event.

Installation
===============

Install event routing backends library or add it to private requirements of your virtual environment ( ``requirements/private.txt`` ).

#. Run ``pip install edx-event-routing-backends``.

#. Run migrations ( ``python manage.py lms migrate`` ).

#. Restart LMS service and celery workers of edx-platform.

Configuration
===============

Two types of configuration are needed for the plugin:

#. Routers for routing transformed events to desired http endpoints.

#. Backends for filtering and transformation of selected events into ``xapi`` or ``caliper`` format.

By default, both ``xapi`` and ``caliper`` backends are already configured along with filters that allow all the supported events. ``caliper`` backend is disabled by default and can be enabled by setting ``CALIPER_EVENTS_ENABLED`` to ``True`` in plugin settings.

Additionally separate log streams for xAPI and Caliper are generated as events are transformed and can be configured to be saved or ignored. These can be configured as described in the `Django docs <https://docs.djangoproject.com/en/4.2/topics/logging/>`_ for the ``xapi_tracking`` and ``caliper_tracking`` loggers.



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

Batching Configuration
----------------------

Batching of events can be configured using the following settings:

#. ``EVENT_ROUTING_BACKEND_BATCHING_ENABLED``: If set to ``True``, events will be batched before being routed. Default is ``False``.
#. ``EVENT_ROUTING_BACKEND_BATCH_SIZE``: Maximum number of events to be batched together. Default is 100.
#. ``EVENT_ROUTING_BACKEND_BATCH_INTERVAL``: Time interval (in seconds) after which events will be ent, whether or not the batch size criteria is met. Default is 60 seconds.

Batching is done in the ``EventsRouter`` backend. If ``EVENT_ROUTING_BACKEND_BATCHING_ENABLED`` is set to ``True``, then events will be batched together and routed to the configured routers after the specified interval or when the batch size is reached, whichever happens first.

In case of downtimes or network issues, events will be queued again to avoid data loss. However, there is no guarantee that the events will be routed in the same order as they were received.

Event bus configuration
-----------------------

The event bus backend can be configured as the producer of the events. In that case, the events will be consumed from the event bus and routed to the configured routers via event bus consumers. The event bus backend can be configured in your edx-platform settings as follows:

.. code-block:: python

    EVENT_TRACKING_BACKENDS["xapi"]["ENGINE"] = "eventtracking.backends.event_bus.EventBusRoutingBackend"
    EVENT_TRACKING_BACKENDS["xapi"]["OPTIONS"]["backends"]["xapi"]["ENGINE"] = "event_routing_backends.backends.sync_events_router.SyncEventsRouter"
    EVENT_TRACKING_BACKENDS["xapi"]["OPTIONS"].pop("backend_name")
    if "openedx_events" not in INSTALLED_APPS:
        INSTALLED_APPS.append("openedx_events")
    SEND_TRACKING_EVENT_EMITTED_SIGNAL = True
    EVENT_BUS_PRODUCER_CONFIG = {
        "org.openedx.analytics.tracking.event.emitted.v1": {
            "analytics": {
                "event_key_field": "tracking_log.name", "enabled": True
            }
        }
    }

Once the event bus producer has been configured, the event bus consumer can be started using the following command:

.. code-block:: bash

    ./manage.py lms consume_events -t analytics -g event_routing_backends --extra '{"consumer_name": "event_routing_backends"}'

OpenEdx Filters
===============

This is an integration that allows to modify current standard outputs by using the `openedx-filters`_ library and is limited to the following filters per processor:


xAPI Filters
------------

+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| Filter                                                                                          | Description                                                                        |
+=================================================================================================+====================================================================================+
| event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor                   | Intercepts and allows to modify the xAPI actor field, this affects all xAPI events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.transformer.xapi_transformer.get_verb                    | Intercepts and allows to modify the xAPI actor field, this affects all xAPI events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.completion_events.completion_created.get_object          | Allows to modify the xAPI object field, this just affects completion events        |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.enrollment_events.base_enrollment.get_object             | Allows to modify the xAPI object field, this just affects enrollment events        |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.exam_events.base_exam.get_object                         | Allows to modify the xAPI object field, this just affects exam events              |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.forum_events.base_forum_thread.get_object                | Allows to modify the xAPI object field, this just affects forum events             |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.grading_events.subsection_graded.get_object              | Allows to modify the xAPI object field, this just affects subsection_graded events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.grading_events.course_graded.get_object                  | Allows to modify the xAPI object field, this just affects course_graded events     |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.link_clicked.get_object                | Allows to modify the xAPI object field, this just affects link_clicked events      |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.outline_selected.get_object            | Allows to modify the xAPI object field, this just affects outline_selected events  |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.tab_navigation.get_object              | Allows to modify the xAPI object field, this just affects tab_navigation events    |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.problem_interaction_events.base_problems.get_object      | Allows to modify the xAPI object field, this just affects problem events           |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.problem_interaction_events.base_problem_check.get_object | Allows to modify the xAPI object field, this just affects problem_check events     |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.video_events.base_video.get_object                       | Allows to modify the xAPI object field, this affects all video events              |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+

.. _event-tracking: https://github.com/openedx/event-tracking

.. _NameWhitelist: https://github.com/openedx/event-tracking/blob/master/eventtracking/processors/whitelist.py

.. _RegexFilter: https://github.com/openedx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

.. _save_statement: https://github.com/openedx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/xapi_lrs_client.py#L70

.. _post: https://github.com/openedx/event-routing-backends/blob/2ec15d054b3b1dd6072689aa470f3d805486526e/event_routing_backends/utils/http_client.py#L67

.. _AsyncRoutingBackend: https://github.com/openedx/event-tracking/blob/fccad3d118f594fe304ec48517e896447f15e782/eventtracking/backends/async_routing.py#L13

.. _CaliperProcessor: https://github.com/openedx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/caliper/transformer_processor.py#L16

.. _XApiProcessor: https://github.com/openedx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/xapi/transformer_processor.py#L16

.. _CaliperEnvelopeProcessor: https://github.com/openedx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/processors/caliper/envelope_processor.py#L12

.. _EventsRouter: https://github.com/openedx/event-routing-backends/blob/ac192ab6b4d1452ada37302d1481eea2f58aef19/event_routing_backends/backends/events_router.py#L15

.. _business_critical_events: https://github.com/openedx/event-routing-backends/blob/e375674156b347be833ad8c2479be2c4ff4b073f/event_routing_backends/helpers.py#L197

.. _edx-celeryutils: https://github.com/openedx/edx-celeryutils

.. _commands: https://github.com/openedx/edx-celeryutils/tree/master/celery_utils/management/commands

.. _openedx-filters: https://github.com/openedx/openedx-filters

