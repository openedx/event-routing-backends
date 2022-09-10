1. Router Configurations Storage
================================

Status
------

Approved

Context
-------

The router will use some sort of configuration to decide what events are
to be sent to what consumers and how. These configurations can be
defined for each partner/enterprise so we could end up having 20-50
configurations.

We have these two options for storing these configurations:

-  Store configurations in Django settings (YAML configuration files).

-  Store configurations in some Django model (database).

Decision
--------

Keeping in mind a large number of enterprise clients, we will store
router configurations in `Django configuration models
<https://github.com/openedx/django-config-models>`__.

Consequences
------------

Storing configurations in `Django configuration
models <https://github.com/openedx/django-config-models>`__ will keep the
settings files cleaner.

Django configuration models have built-in caching support which would
help us address performance-related challenges.

Since enterprise customer management might be done by teams other than
operators, putting these configurations in database will allow us to let
customer support teams manage the settings or could also make make it self
service in future.

Rejected Alternatives
---------------------

**Store configurations in Django settings**

Having too many settings can clutter app settings and would be difficult
to manage.
