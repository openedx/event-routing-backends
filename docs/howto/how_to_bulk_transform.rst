How To Bulk Transform Tracking Logs
===================================

This is a rough guide of how to transform existing tracking log files into the formats supported by event-routing-backends using the ``transform_tracking_logs`` Django management command inside a running LMS installation. Because the transformations perform database access, looking up user, course, and block data, you will need to run this command on the same install of Open edX that created the tracking log files.

.. warning:: This also means that doing large amounts of transformations can cause performance issues on the LMS and downstream learning record stores. Make sure to use the ``--batch_size`` and ``--sleep_between_batches_secs`` options to balance system performance vs load time.

Sources and Destinations
------------------------

For most sources and destinations we use `Apache Libcloud Object storage <https://libcloud.readthedocs.io/en/stable/supported_providers.html>`__ . This should cover casees from local storage to Amazon S3, MinIO, and many other cloud storage solutions. The ``--source_provider`` and ``--destination_provider`` options are the Libcloud Provider names, in all caps (ex: ``S3``, ``LOCAL``, ``MINIO``). The ``--source_config`` and ``--destination_config`` options are JSON strings passed directly to the Libcloud constructor as keyword args.

The ``LRS`` destination provider is a special case that uses the usual event-routing-backends logic for sending events to Caliper and/or xAPI learning record stores.

For the ``LOCAL`` provider, the path to the file(s) is a concatenation of the ``key``, which is the path to a top level directory, a ``container`` which is a single subdirectory name inside the ``key`` directory, and a ``prefix`` (if provided) will be appended to the container to determine the final path.

::

    # This will attempt to recursively read all files in the "/openedx/data/logs/" directory
    {"key": "/openedx/data", "container": "logs"}

    # This will attempt to recursively read all files in "/openedx/data/logs/tracking/" as
    # well as any files in "/openedx/data/logs/" that begin with "tracking"
    {"key": "/openedx/data", "container": "logs", "prefix": "tracking"}

    # This will attempt to read a single file named "/openedx/data/logs/tracking.log"
    {"key": "/openedx/data", "container": "logs", "prefix": "tracking.log"}


For other providers ``key`` and ``secret`` are authentication credentials and ``container`` is roughly synonymous with an S3 bucket. Configuration for each provider is different, please consult the libcloud docs for your provider to learn about other options you may need to pass in to the ``--source_config`` and ``--destination_config`` JSON structures.


Modes Of Operation
------------------

The command can work in a few distinct ways.

**File(s) to learning record store (LRS)** - this will use the existing event-routing-backends configuration to route any log replays to **all** configured LRS backends just like the event was being emitted right now. This can be used to backfill old data, capture old events that didn't previously have transforms, or fix up lost data from downtime issues.

**File(s) to file(s)** - This will perform the same transformations as usual, but instead of routing them to an LRS they can be saved as a file to any libcloud destination. In this mode all events are saved to a single file and no filters are applied.

Additionally all generated statements are written to a Python logger which can be configured to be ignored, save to a file, write standard out, or a log forwarder like `Vector <https://vector.dev/>`__ for more statement handling options. The two loggers are named ``xapi_tracking`` and ``caliper_tracking``, and are always running.

**File(s) to logger** - For any destination you can use the ``--dry_run`` flag to perform tests on finding and transforming data before attempting to store it. Used in conjunction with loggers mentioned above, you can use Python log forwarding without the additional overhead of storing full files.

.. warning::
    Events may be filtered differently in this command than in normal operation. Normally events pass through two layers of filters as described in `getting started <docs/getting_started.rst>`_.

    First are the eventtracking AsyncRoutingBackend can have processor filters, which will be ignored when running this script (since these events have already passed through the eventtracking process).

    Second are the router configuration filters which work on a per-LRS basis. These are respected when the destination is LRS, but ignored when writing to a file and the loggers.


Examples
--------

**Files to LRS**

::

    # Transform all events in the local file /openedx/data/tracking.log to all configured LRSs
    python manage.py lms transform_tracking_logs \
    --source_provider LOCAL \
    --source_config '{"key": "/openedx/data/", "prefix": "tracking.log", "container": "logs"}' \
    --destination_provider LRS \
    --transformer_type xapi

::

    # Transform all events in the local file /openedx/data/tracking.log to all configured LRSs
    # using a smaller batch size and long sleep for LMS performance
    python manage.py lms transform_tracking_logs \
    --source_provider LOCAL \
    --source_config '{"key": "/openedx/data/", "prefix": "tracking.log", "container": "logs"}' \
    --destination_provider LRS \
    --transformer_type caliper \
    --batch_size 1000 \
    --sleep_between_batches_secs 2.5

::

    # Recursively transform any files whose names start with "tracking" from a "logs" directory in the
    # MINIO bucket "logs" to all configured LRSs
    python manage.py lms transform_tracking_logs \
    --source_provider MINIO \
    --source_config '{"key": "openedx", "secret": "[minio secret key]", "container": "openedx", "prefix": "tracking", "host": "minio", "port": 9000, "secure": false}' \
    --destination_provider LRS \
    --transformer_type xapi

    python manage.py lms transform_tracking_logs \
    --source_provider S3 \
    --source_config '{"key": "openedx", "secret": "[minio secret key]", "container": "openedx", "prefix": "tracking", "host": "minio", "port": 9000, "secure": false}' \
    --destination_provider LRS \
    --transformer_type xapi

You can also run these commands using a tutor wrapper:

::
    tutor local run lms python manage.py lms .....

**Files to Files**

::

    # Transform the entire local file /openedx/data/tracking.log to a new file in the local directory
    # /openedx/data/logs/transformed_events/ the file will be named with the current timestamp.
    # Note: The "container" directory must exist!
    python manage.py lms transform_tracking_logs \
    --transformer_type caliper \
    --source_provider LOCAL \
    --source_config '{"key": "/openedx/data/", "container": "logs", "prefix": "tracking.log"}' \
    --destination_provider LOCAL \
    --destination_config '{"key": "/openedx/data/", "container": "transformed_logs", "prefix": "2023-06-01"}'

::

    # Recursively transform any files whose names start with "tracking" from a "tracking_logs" directory in the
    # MinIO bucket "openedx" to a single file in a MinIO storage's "transformed_logs" bucket.
    # ie: http://files.local.overhang.io/openedx/tracking_logs/tracking* to http://files.local.overhang.io/openedx/transformed_logs/2023-06-02/23-06-02_20-29-20_xapi.log
    # This is the configuration for a tutor local environment with MinIO enabled.
    python manage.py lms transform_tracking_logs \
    --source_provider MINIO \
    --source_config '{"key": "openedx", "secret": "minio secret", "container": "openedx", "prefix": "/tracking_logs", "host": "files.local.overhang.io", "secure": false}' \
    --destination_provider MINIO \
    --destination_config '{"key": "openedx", "secret": "minio secret", "container": "openedx", "prefix": "transformed_logs/2023-06-02/", "host": "files.local.overhang.io", "secure": false}' --transformer_type xapi

