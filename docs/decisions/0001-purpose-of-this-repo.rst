1. Purpose of this Repo
=======================

Status
------

Approved

Context
-------

`OEP-26 <https://open-edx-proposals.readthedocs.io/en/latest/oep-0026-arch-realtime-events.html>`__
consists of the following components:

-  Asynchronous Routing Backend

-  Regular-expressions based filter processor

-  IMS Caliper transformer

-  xAPI transformer

-  Router to forward events

Keeping all of these components in one repo will make the repository
unnecessarily tangled since these additional components are not required
by the core app for its functionality.

Decision
--------

Among the components listed above, Asynchronous Routing Backend and the
regular-expressions filter will be added in the core app (i.e.
`event-tracking <https://github.com/openedx/event-tracking>`__) while the
other components, i.e. Caliper transformer backend, xAPI transformer
backend and router, will be added in the current repo.

By keeping the concrete backends separate from the code, we can have
only the core plugin interface for event tracking in its repository.

Consequences
------------

The code will be decoupled and components can be used independently if
required.

Rejected Alternatives
---------------------

**Add the routing backends to the event-tracking repository**

This idea was rejected to keep the core event-tracking repository clean
and independent. The core repo is functional on its own and any
pluggable extensions should be implemented separately.
