event-routing-backends
=============================

|pypi-badge| |travis-badge| |codecov-badge| |doc-badge| |pyversions-badge|
|license-badge|

Various backends for receiving edX LMS events.  The code in this repository
hooks into the `event-tracking`_ app that is installed as a part of
edx-platform. It provides new tracking backends and processors.

.. _event-tracking: https://github.com/edx/event-tracking

Overview (please modify)
------------------------

It provides a backend that can take events and re-transmit them to external
services.  It also provides some new processers that can convert edx-platform
events into other formats.

Currently work to support xAPI and Caliper event formats is in progress.

Documentation
-------------

Documentation for this repo is published to `Read the Docs <https://event-routing-backends.readthedocs.io/en/latest/>`_

License
-------

The code in this repository is licensed under the AGPL 3.0 unless
otherwise noted.

Please see `LICENSE.txt <LICENSE.txt>`_ for details.

How To Contribute
-----------------

Contributions are very welcome.
Please read `How To Contribute <https://github.com/edx/edx-platform/blob/master/CONTRIBUTING.rst>`_ for details.
Even though they were written with ``edx-platform`` in mind, the guidelines
should be followed for all Open edX projects.

The pull request description template should be automatically applied if you are creating a pull request from GitHub. Otherwise you
can find it at `PULL_REQUEST_TEMPLATE.md <.github/PULL_REQUEST_TEMPLATE.md>`_.

The issue report template should be automatically applied if you are creating an issue on GitHub as well. Otherwise you
can find it at `ISSUE_TEMPLATE.md <.github/ISSUE_TEMPLATE.md>`_.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@edx.org.

Getting Help
------------

If you're having trouble, we have discussion forums at https://discuss.openedx.org where you can connect with others in the community.

Our real-time conversations are on Slack. You can request a `Slack invitation`_, then join our `community Slack workspace`_.

For more information about these options, see the `Getting Help`_ page.

.. _Slack invitation: https://openedx-slack-invite.herokuapp.com/
.. _community Slack workspace: https://openedx.slack.com/
.. _Getting Help: https://openedx.org/getting-help

.. |pypi-badge| image:: https://img.shields.io/pypi/v/event-routing-backends.svg
    :target: https://pypi.python.org/pypi/event-routing-backends/
    :alt: PyPI

.. |travis-badge| image:: https://travis-ci.org/edx/event-routing-backends.svg?branch=master
    :target: https://travis-ci.org/edx/event-routing-backends
    :alt: Travis

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
    :target: https://github.com/edx/event-routing-backends/blob/master/LICENSE.txt
    :alt: License
