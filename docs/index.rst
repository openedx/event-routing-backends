.. _Event Routing Home:

Event Routing Backends
######################

.. contents:: :local:

Introduction
------------

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

List of supported edx events and mapping of edx events onto xAPI and Caliper formats can be found in :ref:`supported_events`.

Version information of transformer
----------------------------------

Version of transformer is semantic version of event-routing-backend prefixed with  `event-routing-backends@` included in the statement/event. Version is a string of format "event-routing-backend@X.Y.Z" where increment in X represents breaking changes and increment in Y represents addition/update of fields in the event/statement and Z represents bug fix or patched version.

In xAPI statement, version is in value of the key ``https://w3id.org/xapi/openedx/extension/transformer-version`` in ``extensions`` of ``Context`` of the statement.

In Caliper event, version is in value of the key ``transformerVersion`` in ``extensions`` of the event.


.. toctree::
   :hidden:

   Technial Documentation <technical_documentation/index>


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

