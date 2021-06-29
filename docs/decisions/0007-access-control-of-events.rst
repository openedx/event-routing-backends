Access control of events
========================

Status
------

Pending

Context
-------

`event-routing-backends` can transform edX events in xAPI and Caliper format which can then be routed to concerned organisations. A configureable method is required to filter and route events to relevant organisations.

Decision
--------

#. A method routes events that match the criteria specified in `match_params` in router configurations.

#. `match_params` is a dict comprising of one or more key value pairs.

#. A key in `match_params` need to be an exact match of a key in edx event where hierarchy levels can be separated by '.' (dot).

#. Value of a key in `match_params` can ONLY be a string or a list of strings.

#. Strings in value can be a regular expression. This regular expression will be compared with value of corresponding key in edx event to find a match.

#. `AND` relationship will be assumed between keys a a for successful comparison, if more than one key is specified in `match_params`.

#. `OR` relationship will be assumed between entries of a list in value of a key, for a successful comparison.

Examples
--------

1. Following configuration will transform and emit an edX event if `context[org_id]` is `edX` AND event `name` is `problem_check` OR `showanswer` OR `stop_video`.

::

    "match_params": {
                    "context.org_id": "edX",
                    "name": ["problem_check", "showanswer", "stop_video"]}

