Change Log
----------

..
   All enhancements and patches to event_routing_backends will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

*

[5.2.1]
~~~~~~~

* Added `video_complete` event to xAPI backend and fixed broken links in documentation

[5.2.0]
~~~~~~~

* Added Support for Django4 and used djfernet instead of django-fernet-fields
* Removed Django22, 30 and 31 support
* Constrained "click" to 7.1.2 as edx-celeryutils constraints the version to this package 


[4.1.1]
~~~~~~~

* Switched from jsonfield2 to jsonfield as the earlier one has archived and merged back in the latter one.

[4.1.0]
~~~~~~~

* Added support for django3.0, 3.1 and 3.2

[4.0.1]
~~~~~~~

* Change a noisy INFO log message in ``TransformerRegistry.register()`` to DEBUG and fix two logging typos.

[4.0.0]
~~~~~~~

* **Breaking change**: Rename ``CaliperEnvelopProcessor`` to ``CaliperEnvelopeProcessor`` and rename module accordingly (typo fix)

[3.0.2]
~~~~~~~
* Added more directions for local testing
* changed how event data is enveloped for caliper events
* changed url to point from http://purl.imsglobal.org/ctx/caliper/v1p1 to http://purl.imsglobal.org/ctx/caliper/v1p2

[3.0.1]
~~~~~~~

This tag is a re-release of version 3.0.0. (Failed to bump internal version, though.)

[3.0.0]
~~~~~~~

* **Breaking change**: Caliper and xAPI processors will reject events unless the ``CALIPER_EVENTS_ENABLED`` and ``XAPI_EVENTS_ENABLED`` Django settings are enabled, respectively.


[2.0.0]
~~~~~~~

(no changelog recorded)

[1.0.0] - 2020-11-09
~~~~~~~~~~~~~~~~~~~~

* Dropped support for Python 3.5

[0.2.0] - 2020-11-06
~~~~~~~~~~~~~~~~~~~~

* caliper transformer backend
* event routing backend

[0.1.0] - 2020-09-22
~~~~~~~~~~~~~~~~~~~~

* First release on PyPI.
