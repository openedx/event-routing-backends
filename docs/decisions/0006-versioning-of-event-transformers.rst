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

#. The "transformer version" will be a concatenation of the name of the transformer ("event-routing-backends"), an @ symbol, and the symantic version of the event-routing-backends package used to generate the event.

#. This combined version "event-routing-backends@v(X.Y.Z)" can be found in ``context [ extensions [ https://w3id.org/xapi/openedx/extension/transformer-version ] ]`` for xAPI statement and in ``extensions [ transformerVersion ]`` for Caliper event.

#. Transformer version number will be the semantic version of the event-routing-backends package.

#. The event-routing-backends major version will be incremented when:

   #. Transformer is changed due to update in original specification (xAPI or Caliper).

   #. A key is removed from or renamed in the existing transformer.

   #. Value of a key is updated in the existing transformer.

#. The event-routing-backends minor version will be incremented when:

   #. A key is added to an existing transformer.
   #. A new event is added for transformation.

#. Minor version (Z) will be incremented when:

   #. A bug is fixed.

#. Change logs of transformers will be maintained for both xAPI and Caliper.


Changelog
---------
- Updated 2023-02-28 to change the format of the transformer version.
   - The previous version named the key "eventVersion", but the actual implementation used URL key pointing to the event-routing-backends docs. It was decided that since the version number represents the actual version of the event-routing-backends package and not the version of a specific event, this rename could tackle both issues.
