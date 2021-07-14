Persistence and retries for events
==================================

Status
------

Pending

Context
-------

`event-routing-backends` transmits events to configured Learning Record Consumer (LRC) via http protocol in near real-time. A strategy needs to be implemented to handle the case when an LRC's link is down.

Decision
--------

1. Retry attempts shall be made for all events for a configured limit of time and number of retries.

2. A limited type of events (lets call them persisted events) shall be stored in a database after all retry attempts have been exhausted. List of persisted events shall contain events that an LRC may use for record keeping such as course enrolment and completion events.

3. A scheduled process will retry transmitting all persisted events in the database to respective LRC(s) at a configured frequency (e.g. once a day).

4. The persisted events will be deleted from the database after a configured amount of time (e.g. 30 days).

5. An interface shall be provided for admin to view the list of LRC(s) whose events are persisting in the database. The admin may choose to contact the LRC(s) to try and resolve the communication issue.
