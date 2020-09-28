1. Binding app for Caliper
==========================

Status
------

Approved

Context
-------

We need to decide some approach to encapsulate and structure the Caliper
events. We have the following options for binding caliper events:

-  Make our own data structure to store a caliper event (e.g. a python dict)

-  Use IMS’ `caliper-python <https://github.com/IMSGlobal/caliper-python>`__ library

Decision
--------

We will be using python dictionaries for processing and encapsulation of
transformed events to keep things simple.

Consequences
------------

Python dictionaries will be used for binding Caliper events. These
events stored as python dictionaries can be converted into JSON later
and sent to interested consumers.

Rejected Alternatives
---------------------

**Use IMS’ caliper-python library**

The library under discussion is not published on
`PyPI <https://pypi.org/search/?q=caliper>`__. We’d have to fork the
repo and add its dependency on our app. Therefore we won’t be using this
library.
