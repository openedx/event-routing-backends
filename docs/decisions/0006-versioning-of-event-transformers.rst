Versioning of event transformers
================================

Status
------

Pending

Context
-------

Event transformers may undergo modification in future in response to consumer request, change in specification, bug fixes etc.

Decision
--------
#. Versions of event transformers will be maintained and emitted as part of  xAPI and Caliper events.

#. Transformer version will be defined by two non-negative integers X and Y representing major and minor version respectively in the form: X.Y.

#. Major version (X) will be incremented when:

   #. Transformer is changed due to update in original specification (xAPI or Caliper).

   #. A key is removed from or renamed in the existing transformer.

   #. Value of a key is updated in the existing transformer.

#. Minor version (Y) will be incremented when:

   #. A key is added to an existing transformer.

#. Change logs of transformers will be maintained for both xAPI and Caliper.

#. This version (X.Y) can be found in `` context [ extensions [ minorVersion ] ]`` for xAPI statement and in ``extensions [ minorVersion ]`` for Caliper event.
