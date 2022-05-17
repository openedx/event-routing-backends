Access control of events
========================

Status
------

Approved

Context
-------

`event-routing-backends` can transform filtered edX events in xAPI and Caliper format which can then be routed to configured URLs. Procedure for configuring URLs of learning record consumers can be found in the :ref:`Installation`. List of supported edX events can be accessed `here`_. A method is required to filter edX events based on event name, course id, organisation id etc. or on any combination of these properties.

Decision
--------

#. A method will be created that filters events that match the criteria specified in `match_params` in router configurations.

#. `match_params` is a dict comprising of one or more key value pairs.

#. A key in `match_params` need to be an exact match of a key in edX event where hierarchy levels can be separated by '.' (dot).

#. Value of a key in `match_params` can ONLY be a string or a list of strings.

#. Strings in value can be a regular expression. This regular expression will be compared with value of corresponding key in edX event to find a match.

#. `AND` relationship will be assumed between keys a for successful comparison, if more than one key is specified in `match_params`.

#. `OR` relationship will be assumed between entries of a list in value of a key, for a successful comparison.

Examples
--------

1. Following configuration will allow transformation and routing of an edX event if `context[org_id]` is `edX` AND event name is `problem_check` OR `showanswer` OR `stop_video`.

::

    "match_params": {
             "context.org_id": "edX",
             "name": ["problem_check", "showanswer", "stop_video"]}

2. Following configuration will allow transformation and routing of an edX event if the content organisation is `edX` AND course run is `2021` AND event name starts with `problem` OR event name contains `video`.

::

    "match_params": {
             "course_id": "^.*course-v.:edX\+.*\+2021.*$",
             "name": ["^problem.*", "video"]}

3. Following configuration will allow transformation and routing of an edX event if the enterprise is `org_XYZ` AND event name is `edx.course.completed` OR `edx.course.enrollment.activated`.

::

    "match_params": {
             "enterprise_uuid": "org_XYZ",
             "name": ["edx.course.completed", "edx.course.enrollment.activated"]}

.. _here: ../event-mapping/Supported_events.rst
