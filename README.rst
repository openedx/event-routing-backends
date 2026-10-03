event-routing-backends
=============================

|pypi-badge| |ci-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Various backends for retransmitting edX LMS events to external services.

Overview
--------

event-routing-backends contains plugins for the `event-tracking`_ app that is installed as a part of edx-platform. It provides a backend that can take events and re-transmit them to external services.  It also provides some new processers that can convert edx-platform events into other formats.

Currently work to support xAPI and Caliper event formats is in progress.

See `OEP 26`_ for background; the xAPI and Caliper subdocuments in particular include a specification of how LMS events will be translated to the format of the respective protocols.

.. _event-tracking: https://github.com/openedx/event-tracking
.. _OEP 26: https://open-edx-proposals.readthedocs.io/en/latest/oep-0026-arch-realtime-events.html

Documentation
-------------

Documentation for this repo is published to `Read the Docs <https://event-routing-backends.readthedocs.io/en/latest/>`_

Credential-free delivery diagnostics
-----------------------------------

Event deliveries contain routing credentials and event payloads. Configure the
supported logging filter in Django's ``LOGGING`` setting before collecting
these diagnostics::

    LOGGING["filters"]["event_delivery"] = {
        "()": "event_routing_backends.security.CredentialSafeEventRoutingFilter",
    }
    for name in ("celery.app.trace", "event_routing_backends.tasks",
                 "event_routing_backends.utils.http_client",
                 "event_routing_backends.utils.xapi_lrs_client"):
        entry = LOGGING["loggers"].setdefault(name, {})
        entry.setdefault("filters", []).append("event_delivery")
    for handler in LOGGING["handlers"].values():
        handler.setdefault("filters", []).append("event_delivery")

Logger coverage protects Celery worker handler replacement; handler coverage
also protects records propagated by additional event-routing children. The
filter retains severity, source location and validated task correlation while
withholding message payloads, exception text and arbitrary structured extras.
It does not alter records for unrelated applications or Celery tasks.

Persistent delivery failures retain their task name and ID in native
``FailedTask`` rows, with empty invocation arguments and a constant exception.
These rows are diagnostic-only: ``FailedTask.reapply`` refuses them before
submission. Recover from the original tracking logs with current routing
configuration using ``recover_failed_events`` instead. This change does not
sanitize already-stored failure rows or alter their retention.

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

How To Contribute
-----------------

Contributions are very welcome.
Please read `How To Contribute <https://github.com/openedx/.github/blob/master/CONTRIBUTING.md>`__ for details.
should be followed for all Open edX projects.

The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@openedx.org.

Getting Help
------------

If you're having trouble, we have discussion forums at https://discuss.openedx.org where you can connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our `community Slack workspace`_.

For more information about these options, see the `Getting Help <https://openedx.org/getting-help>`__ page.

.. _Slack invitation: https://openedx.org/slack
.. _community Slack workspace: https://openedx.slack.com/

.. |pypi-badge| image:: https://img.shields.io/pypi/v/event-routing-backends.svg
    :target: https://pypi.python.org/pypi/event-routing-backends/
    :alt: PyPI

.. |ci-badge| image:: https://github.com/openedx/event-routing-backends/workflows/Python%20CI/badge.svg?branch=master
    :target: https://github.com/openedx/event-routing-backends/actions?query=workflow%3A%22Python+CI%22
    :alt: CI

.. |codecov-badge| image:: https://codecov.io/github/edx/event-routing-backends/coverage.svg?branch=master
    :target: https://codecov.io/github/edx/event-routing-backends?branch=master
    :alt: Codecov

.. |doc-badge| image:: https://readthedocs.org/projects/event-routing-backends/badge/?version=latest
    :target: https://event-routing-backends.readthedocs.io/en/latest/
    :alt: Documentation

.. |pyversions-badge| image:: https://img.shields.io/pypi/pyversions/event-routing-backends.svg
    :target: https://pypi.python.org/pypi/event-routing-backends/
    :alt: Supported Python versions

.. |license-badge| image:: https://img.shields.io/github/license/edx/event-routing-backends.svg
    :target: https://github.com/openedx/event-routing-backends/blob/master/LICENSE.txt
    :alt: License
