PII leakage prevention
================================

Status
------

Accepted

Context
-------

``Event-routing-backends`` transforms and emits edx events that may contain PII which is not meant to be shared with learning record consumers. New xAPI and Caliper transformers are expected to be added in ``Event-routing-backends`` and therefore, a mechanism needs to be put in place to reduce chances of PII leakage via these transformers.

Decision
--------
#. An accessor `method`_ will be developed to get values from open edx events for a specified key. Information inside the open edx event will only be accessed using this accessor method in base transformers and in event transformers.

#. If a key, required by the specification (xAPI or Caliper), is not found in open edx event, this method will throw an exception.

#. If a key, deemed optional by the specification (xAPI or Caliper), is not found in open edx event, this method will log this instance and return None.

#. The efficacy of fuzzy comparison between keys in transformed events and potential PII keys will be evaluated in future and incorporated if found useful.

Benefits
---------

#. Only the instances where this accessor is called, will need to be reviewed during code review, in order to check for potential PII leakage.

.. _method: https://github.com/openedx/event-routing-backends/blob/f430d4cf58bdab01e42fcc944241898606873d82/event_routing_backends/processors/mixins/base_transformer.py#L139
