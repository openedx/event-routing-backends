Persistence and retries for events
==================================

Status
------

Approved

Context
-------

`event-routing-backends` transmits events to configured recipients (Learning Record Stores) via http protocol in near real-time. A strategy needs to be implemented to handle the case when an LRS's link is down.

Decision
--------

1. A celery task will be created for each transformation (xAPI or Caliper) of an event. Once the transformation is complete, nested celery tasks will be created, one for each recipient, to route the event.

2. Retry attempts shall be made for each recipient, for all events types, and for a configured number of retries and delay between each retry.

3. A limited type of events (namely *business critical events*) shall be persisted even after all retry attempts have been exhausted. Celery tasks, that failed to route the transformed event to their intended recipients, will be stored in a database. Each of these tasks (persisted via `celery-utils`) will include just enough information about the event that it gets resent appropriately after persistence. Events that consumers of LRS may use for record keeping such as course enrollment and completion events, shall be classified as *business critical events*.

4. A scheduled process will retry transmitting all persisted events in the database to respective recipient(s) at a configured frequency (e.g. once a day). This process will also check if the number of persisted events is higher than a configured threshold. If so, it will generate an alert for the admin.

5. An interface shall be provided for admin to view the list of recipient(s) whose events are persisting in the database. The admin may choose to contact the recipient(s) to try and resolve the communication issue.

Consequences
------------

1. All but *business critical events*, will be lost after the time and number of retry attempts in decision # 2 expire.

2. Decision # 1 is necessary to enable decision # 3 but will also increase the number of celery workers in use.

3. The admin will need to respond to alert discussed in decision # 4 to avoid unnecessary utilisation of storage space.
