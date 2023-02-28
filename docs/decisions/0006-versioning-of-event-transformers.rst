Versioning of event transformers
================================

Status
------

Accepted

Context
-------

Event transformers may undergo modification in future in response to consumer request, change in specification, bug fixes etc.

Decision
--------
#. Versions of event transformers will be maintained and emitted as part of xAPI and Caliper events.

#. The "transformer version" will be a concatenation of the name of the transformer ("event-routing-backends"), an @ symbol, and the version of the event-routing-backends package used to generate the event.

#. This combined version "event-routing-backends@v(X.Y)" can be found in ``context [ extensions [ transformerVersion ] ]`` for xAPI statement and in ``extensions [ transformerVersion ]`` for Caliper event.

#. Transformer version number will be defined by two non-negative integers X and Y representing major and minor version respectively in the form: X.Y.

#. Major version (X) will be incremented when:

   #. Transformer is changed due to update in original specification (xAPI or Caliper).

   #. A key is removed from or renamed in the existing transformer.

   #. Value of a key is updated in the existing transformer.

#. Minor version (Y) will be incremented when:

   #. A key is added to an existing transformer.

#. Change logs of transformers will be maintained for both xAPI and Caliper.

Changelog
---------
- Updated 2023-02-28 to change the format of the transformer version.
   - The previous version named the key "eventVersion", but the actual implementation used URL key pointing to the event-routing-backends docs. It was decided that since the version number represents the actual version of the event-routing-backends package and not the version of a specific event, this rename could tackle both issues.
