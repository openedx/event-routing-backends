4. Transformers Architecture
============================

Status
------

Approved

Context
-------

We can develop event transformers either using the “Backend” architecture
or “Processor” architecture. Making the transformers “backends” will result
in relatively more nesting in the configurations as this “backend” will have
its own configurations.

If we decide to develop the event transformers as “processors”, it will result
in less complexity in the code since the transformer can be easily appended in
any backend’s (router or logger) processors’ pipeline.


Decision
--------

Transformers will be developed as event processors that can be added in
any backend’s pipeline. Then the transformed events can be used for any purpose,
either for simply logging using the LoggerBackend or to route events using
EventRoutingBackend.

Consequences
------------

Developing transformers as processors will result in relatively less complex
configurations and it would provide us wider range of use cases for the transformers.
