Persistence and retries for events
==================================

Status
------

Pending

Context
-------

`event-routing-backends` transmits events to configured Learning Record Store (LRS) via http protocol in near real-time. A strategy needs to be implemented to handle the case when an LRS's link is down.

Decision
--------

1. Retry attempts shall be made for all events for a configured limit of time and number of retries.

2. A limited type of events (namely *business critical events*) shall be persisted even after all retry attempts have been exhausted. The celery task for routing these events to the LRS (whose link is down) will be stored in a database. List of persisted events shall contain events that consumers of LRS may use for record keeping such as course enrolment and completion events.

3. A scheduled process will retry transmitting all persisted events in the database to respective LRS(s) at a configured frequency (e.g. once a day). This process will also check if the number of persisted events is higher than a configured threshold. If so, it will generate an alert.

4. An interface shall be provided for admin to view the list of LRS(s) whose events are persisting in the database. The admin may choose to contact the LRS(s) to try and resolve the communication issue.

Consequences
------------

1. All but *business critical events*, will be lost after the time and number of retry attempts mentioned in decision #1 expire.

2. The admin will need to respond to alert discussed in #3 to avoid unnecessary utilisation of storage space.

3. A new celery task will be used for routing each transformed event to its respective LRS. This will enable #2 but will also increase the number of celery workers in use.
