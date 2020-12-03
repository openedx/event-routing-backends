===========
How To Test
===========

This is a rough guide of how to go about testing backends in edx-platform. It assumes you have devstack already up and running. If not, see `devstack docs <https://github.com/edx/devstack>`_.


Add edx-event-routing-backends to requirements
----------------------------------------------

There is a chance some of this has already been done:

- Add edx-event-routing-backends to requirements/edx/base.in and run make upgrade in lms shell(to enter shell, call `make lms-shell`).

- Install the requirements using: `make requirements`

If you are locally developing on events-routing-backends while testing it in edx-platform:

- Clone events-routing-backends into ${DEVSTACK_WORKSPACE}/src and pip install from local directory using ::

    $ pip install -e /edx/src/*/events-routing-backends     # this is run from within lms docker shell



Add events-routing-backends app to Installed Apps in LMS and/or CMS
-------------------------------------------------------------------

There is a chance some of this has already been done:

- Edit INSTALLED_APPS variable in <lms | cms>/envs/common.py and add::

    'event_routing_backends.apps.EventRoutingBackendsConfig'

Configure for testing
---------------------

Follow instructions in `getting_started <docs/gettingstarted.rst>`_ doc. There is a chance some of this has already been done. Most of the code changes should just be copy and paste, but here are some suggested changes for debugging. It'll be easier to understand following instructions if you read `getting_started <docs/gettingstarted.rst>`_ doc first.

Change router endpoint
~~~~~~~~~~~~~~~~~~~~~~

When adding configurations for router, change host_configuration.url key to point to a link at `webhook.site <webhook.site>`_. When you visit the site, it will automatically generate an unique link for you. Use the unique url as value for host_configuration.url key.

Filtering events
~~~~~~~~~~~~~~~~

There are two ways you can filter events:

- Event types can be filtered using `RegexFilter`_ in EVENT_TRACKING_BACKENDS.${backend_name}.OPTIONS.processors.OPTIONS

.. _RegexFilter: https://github.com/edx/event-tracking/blob/master/eventtracking/processors/regex_filter.py

- Particular instances of event types can be filtered based on key, value pair in the serialized event dict. When setting up router in django admin, add key, value pair you want to match_params. If you want all instances of events to be sent, set match_params to empty dict: `match_params: {}`

Triggering events
-----------------

LMS throws ton of events. You'll have to do something different for each event type you are testing. You can find which type of events are supported at event_routing_backends/processors/${processor_name}/event_transformers.

For my testing, I tested using navigation events, so I just navigated around a local course using the navigation bar and it created events every time I moved around.
