Getting Started
===============

Setup
-----


``event-routing-backends`` is developed as a pluggable application for the edx-platform. The code in this app
hooks into the `event-tracking`_ app that is installed as a part of
edx-platform. It provides new tracking backends and processors.

.. _event-tracking: https://github.com/edx/event-tracking

- Add ``event_routing_backends.apps.EventRoutingBackendsConfig`` to ``INSTALLED_APPS`` in ``lms/envs/common.py``.
- Update ``EVENT_TRACKING_BACKENDS`` setting to include backend configuration. See sample configuration for ``caliper`` backend below.

Events can be filtered with `RegexFilter`_. For example in this configuration we allowing
only enrollment, seek_video and edx.video.position.changed events to be routed to caliper event store.

.. _RegexFilter: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

   .. code-block:: python

    EVENT_TRACKING_BACKENDS = {
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
                                    'ENGINE': 'event_routing_backends.processors.caliper.envelop_processor.CaliperEnvelopProcessor',
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
    }

- Run migrations in lms-shell
   .. code-block:: bash

    $ ./manage.py lms migrate event_routing_backends

- Add router configuraton from django admin under ``EVENT_ROUTING_BACKENDS`` section (http://localhost:18000/admin/event_routing_backends/routerconfiguration/add/) using backend name ``caliper``

  Here is a sample configuration for a `Bearer Authentication`_ client which routes only those events where ``org_id`` is set to edX.
  `override_args` allows us to pass any additional info in event.

  .. _Bearer Authentication: https://swagger.io/docs/specification/authentication/bearer-authentication/

  .. code-block:: JSON

    [
        {
            "override_args": {
                "sensor": "test.sensor.example.com",
                "new_key": "new_value"
            },
            "host_configurations": {
                "auth_key": "test_key",
                "url": "http://concerned.host.example.com",
                "auth_scheme": "Bearer",
                "headers": {
                    "test": "header"
                }
            },
            "router_type": "AUTH_HEADERS",
            "match_params": {
                "context.org_id": "edX"
            }
        }
    ]


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
