.. _configuration:

Configuration
#############

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

.. _RegexFilter: https://github.com/openedx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

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

.. _NameWhiteList: https://github.com/openedx/event-tracking/blob/master/eventtracking/processors/whitelist.py

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
