"""
Tests for the transform_tracking_logs management command.
"""
import json
import os
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from libcloud.storage.types import ContainerDoesNotExistError

import event_routing_backends.management.commands.transform_tracking_logs as transform_tracking_logs
from event_routing_backends.management.commands.helpers.queued_sender import QueuedSender
from event_routing_backends.management.commands.transform_tracking_logs import (
    _get_chunks,
    get_dest_config_from_options,
    get_libcloud_drivers,
    get_source_config_from_options,
    validate_source_and_files,
)

LOCAL_CONFIG = json.dumps({"key": "/openedx/", "container": "data", "prefix": ""})
REMOTE_CONFIG = json.dumps({
    "key": "api key",
    "secret": "api secret key",
    "prefix": "/xapi_statements/",
    "container": "test_bucket",
    "secure": False,
    "host": "127.0.0.1",
    "port": 9191
})


@pytest.fixture
def mock_common_calls():
    """
    Mock out calls that we test elsewhere and aren't relevant to the command tests.
    """
    command_path = "event_routing_backends.management.commands.transform_tracking_logs"
    helper_path = "event_routing_backends.management.commands.helpers"
    with patch(command_path+".Provider") as mock_libcloud_provider:
        with patch(command_path+".get_driver") as mock_libcloud_get_driver:
            with patch(helper_path + ".queued_sender.EventsRouter") as mock_eventsrouter:
                yield mock_libcloud_provider, mock_libcloud_get_driver, mock_eventsrouter


def command_options():
    """
    A fixture of different command options and their expected outputs.
    """
    options = [
        # Local file to LRS, small batch size to test batching
        {
            "transformer_type": "xapi",
            "source_provider": "LOCAL",
            "source_config": LOCAL_CONFIG,
            "batch_size": 1,
            "sleep_between_batches_secs": 0,
            "chunk_size": 1024,  # We use this to override the default size of bytes to download
            "expected_results": {
                "expected_batches_sent": 2,
                "log_lines": [
                    "Looking for log files in data/*",
                    "Max queue size of 1 reached, sending.",
                    "Sending 1 events to LRS...",
                    "Queued 2 log lines, could not parse 2 log lines, skipped 8 log lines, sent 3 batches.",
                    "Sending to LRS!"
                ]
            },
        },
        # Remote file to LRS dry run no batch size
        {
            "transformer_type": "xapi",
            "source_provider": "MINIO",
            "source_config": REMOTE_CONFIG,
            "sleep_between_batches_secs": 0,
            "dry_run": True,
            "expected_results": {
                # Dry run, nothing should be sent
                "expected_batches_sent": 0,
                "log_lines": [
                    "Looking for log files in test_bucket/xapi_statements/*",
                    "Finalizing 2 events to LRS",
                    "Dry run, skipping final storage.",
                    "Queued 2 log lines, could not parse 2 log lines, skipped 8 log lines, sent 0 batches.",
                ]
            },
        },
        # Remote file to LRS, default batch size
        {
            "transformer_type": "xapi",
            "source_provider": "MINIO",
            "source_config": REMOTE_CONFIG,
            "sleep_between_batches_secs": 0,
            "expected_results": {
                # No batch size given, default is 10k so only one batch sent
                "expected_batches_sent": 1,
                "log_lines": [
                    "Looking for log files in test_bucket/xapi_statements/*",
                    "Finalizing 2 events to LRS",
                    "Sending to LRS!",
                    "Sending 2 events to LRS...",
                    "Queued 2 log lines, could not parse 2 log lines, skipped 8 log lines, sent 1 batches.",
                ]
            },
        },
        # Local file to remote file
        {
            "transformer_type": "xapi",
            "source_provider": "MINIO",
            "source_config": REMOTE_CONFIG,
            "destination_provider": "MINIO",
            "destination_config": REMOTE_CONFIG,
            "batch_size": 2,
            "sleep_between_batches_secs": 0,
            "expected_results": {
                # Remote files only get written once
                "expected_batches_sent": 1,
                "log_lines": [
                    "Looking for log files in test_bucket/xapi_statements/*",
                    "Finalizing 0 events to",
                    "Storing via Libcloud!",
                    "Max queue size of 2 reached, sending.",
                    "Storing 2 events to libcloud destination test_bucket/xapi_statements/",
                    "Storing 0 events to libcloud destination test_bucket/xapi_statements/",
                    "Queued 2 log lines, could not parse 2 log lines, skipped 8 log lines, sent 2 batches.",
                ]
            },
        },
        # Remote file dry run
        {
            "transformer_type": "xapi",
            "source_provider": "MINIO",
            "source_config": REMOTE_CONFIG,
            "destination_provider": "MINIO",
            "destination_config": REMOTE_CONFIG,
            "batch_size": 1,
            "dry_run": True,
            "sleep_between_batches_secs": 0,
            "expected_results": {
                # Dry run, nothing should be sent
                "expected_batches_sent": 0,
                "log_lines": [
                    "Looking for log files in test_bucket/xapi_statements/*",
                    "Finalizing 0 events to",
                    "Dry run, skipping, but still clearing the queue.",
                    "Dry run, skipping final storage.",
                    "Queued 2 log lines, could not parse 2 log lines, skipped 8 log lines, sent 0 batches.",
                ]
            },
        },
    ]

    for option in options:
        yield option


def _get_tracking_log_file_path():
    TEST_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    return '{test_dir}/fixtures/tracking.log'.format(test_dir=TEST_DIR_PATH)


def _get_raw_log_size():
    tracking_log_path = _get_tracking_log_file_path()
    return os.path.getsize(tracking_log_path)


def _get_raw_log_stream(_, start_bytes, end_bytes):
    """
    Return raw event json parsed from current fixtures
    """
    tracking_log_path = _get_tracking_log_file_path()
    with open(tracking_log_path, "rb") as current:
        current.seek(start_bytes)
        yield current.read(end_bytes - start_bytes)


@pytest.mark.parametrize("command_opts", command_options())
def test_transform_command(command_opts, mock_common_calls, caplog, capsys):
    """
    Test the command and QueuedSender with a variety of options.
    """
    mock_libcloud_provider, mock_libcloud_get_driver, mock_eventsrouter = mock_common_calls

    expected_results = command_opts.pop("expected_results")
    transform_tracking_logs.CHUNK_SIZE = command_opts.pop("chunk_size", 1024*1024*2)

    mm = MagicMock()

    mock_log_object = MagicMock()
    mock_log_object.__str__.return_value = "tracking.log"
    mock_log_object.name = "tracking.log"
    mock_log_object.size = _get_raw_log_size()

    # Fake finding one log file in each container, it will be loaded and parsed twice
    mm.return_value.iterate_container_objects.return_value = [mock_log_object]
    mm.return_value.download_object_range_as_stream = _get_raw_log_stream
    mock_libcloud_get_driver.return_value = mm

    mm2 = MagicMock()
    # Fake a router mapping so some events in the log are actually processed
    mm2.registry.mapping = {"problem_check": 1}
    # Fake a process response that can be serialized to json
    mm2.return_value = {"foo": "bar"}
    mock_eventsrouter.return_value.processors = [mm2]

    call_command(
        'transform_tracking_logs',
        **command_opts
    )

    # Router should only be set up once
    assert mock_eventsrouter.call_count == 1

    captured = capsys.readouterr()
    print(captured.out)

    # Log statements we always expect with this configuration
    assert "Streaming file tracking.log..." in captured.out

    # There are intentionally broken log statements in the test file that cause these
    # lines to be emitted.
    assert "EXCEPTION!!!" in caplog.text
    assert "'NoneType' object has no attribute 'group'" in caplog.text
    assert "Expecting ',' delimiter: line 1 column 63 (char 62)" in caplog.text

    # Check the specific expected log lines for this set of options
    for line in expected_results["log_lines"]:
        assert line in caplog.text or line in captured.out


def test_queued_sender_store_on_lrs(mock_common_calls, capsys):
    """
    Test that we don't attempt to store on an LRS backend.
    """
    qs = QueuedSender("LRS", "fake_container", None, "xapi")
    qs.store()

    captured = capsys.readouterr()
    print(captured.out)
    assert "Store is being called on an LRS destination, skipping." in captured.out


def test_queued_sender_broken_event(mock_common_calls, capsys):
    """
    Test that we don't attempt to store on an LRS backend.
    """
    qs = QueuedSender("LRS", "fake_container", None, "xapi")
    assert not qs.is_known_event({"this has no name key and will fail": 1})


def test_queued_sender_store_empty_queue(mock_common_calls, capsys):
    """
    Test that we don't attempt to store() when there's nothing in the queue.
    """
    qs = QueuedSender("NOT LRS", "fake_container", None, "xapi")
    qs.finalize()

    captured = capsys.readouterr()
    print(captured.out)
    assert "Nothing in the queue to store!" in captured.out


def test_queued_sender_send_on_libcloud(mock_common_calls, capsys):
    """
    Test that we don't attempt to send() when using a libcloud backend.
    """
    qs = QueuedSender("NOT LRS", "fake_container", None, "caliper")
    qs.send()

    captured = capsys.readouterr()
    print(captured.out)
    assert "Skipping send, we're storing with libcloud instead of an LRS." in captured.out


def test_queued_sender_container_does_not_exist(mock_common_calls, caplog):
    """
    Test that we raise an exception if a container doesn't exist.
    """
    mock_destination = MagicMock()
    mock_destination.get_container.side_effect = ContainerDoesNotExistError(
        "Container 'fake_container' doesn't exist.", None, "fake")
    with pytest.raises(ContainerDoesNotExistError):
        qs = QueuedSender(mock_destination, "fake_container", "fake_prefix", "xapi")
        qs.queued_lines = ["fake"]
        qs.store()


def test_invalid_libcloud_source_driver(capsys, mock_common_calls):
    """
    Check error cases when non-existent libcloud drivers are passed in.
    """
    mock_libcloud_provider, mock_libcloud_get_driver, mock_eventsrouter = mock_common_calls

    mock_libcloud_get_driver.side_effect = [AttributeError(), MagicMock()]

    with pytest.raises(AttributeError):
        get_libcloud_drivers("I should fail", {}, "I should never get called", {})

    captured = capsys.readouterr()
    print(captured.out)
    assert "is not a valid source Libcloud provider." in captured.out


def test_invalid_libcloud_dest_driver(capsys, mock_common_calls):
    mock_libcloud_provider, mock_libcloud_get_driver, mock_eventsrouter = mock_common_calls

    mock_libcloud_get_driver.side_effect = [MagicMock(), AttributeError()]
    with pytest.raises(AttributeError):
        get_libcloud_drivers("I should succeed", {}, "I should fail", {})

    captured = capsys.readouterr()
    print(captured.out)
    assert "is not a valid destination Libcloud provider." in captured.out


def test_no_files_in_source_dir(caplog):
    """
    Check error case when there are no source files found in the libcloud source.
    """
    fake_driver = MagicMock()
    fake_driver.iterate_container_objects.return_value = []
    with pytest.raises(FileNotFoundError):
        validate_source_and_files(fake_driver, "container name", "prefix")


def test_required_source_libcloud_keys(capsys):
    """
    Check that we raise an error if the container and prefix aren't given.
    """
    with pytest.raises(KeyError):
        get_source_config_from_options("{}")

    captured = capsys.readouterr()
    print(captured.out)
    assert "The following keys must be defined in source_config: 'prefix', 'container'" in captured.out


def test_required_dest_libcloud_keys(capsys):
    """
    Check that we raise an error if the container and prefix aren't given in a non-LRS destination.
    """
    with pytest.raises(KeyError):
        get_dest_config_from_options(None, "{}")

    captured = capsys.readouterr()
    print(captured.out)
    assert "If not using the 'LRS' destination, the following keys must be defined in destination_config: " \
           "'prefix', 'container'" in captured.out


def test_get_source_config():
    """
    Check that our special keys are popped off the options when retrieving the source config.
    """
    options = {
        "key": "fake test key",
        "container": "fake container",
        "prefix": "fake prefix"
    }

    config, container, prefix = get_source_config_from_options(json.dumps(options))

    assert len(config) == 1
    assert config["key"] == options["key"]
    assert container == "fake container"
    assert prefix == "fake prefix"


def test_get_dest_config():
    """
    Check that our special keys are popped off the options when retrieving the non-LRS destination config.
    """
    options = {
        "key": "fake test key",
        "container": "fake container",
        "prefix": "fake prefix"
    }

    config, container, prefix = get_dest_config_from_options("fake provider", json.dumps(options))

    assert len(config) == 1
    assert config["key"] == options["key"]
    assert container == "fake container"
    assert prefix == "fake prefix"


def test_get_dest_config_lrs():
    """
    Check that an LRS destination config returns appropriate values.
    """
    options = {}

    config, container, prefix = get_dest_config_from_options("LRS", options)
    assert config is None
    assert container is None
    assert prefix is None


def test_get_chunks():
    """
    Tests the retry functionality of the get_chunks function.
    """
    fake_source = MagicMock()
    fake_source.download_object_range_as_stream.return_value = "abc"

    # Check that we got the expected return value
    assert _get_chunks(fake_source, "", 0, 1) == "abc"
    # Check that we broke out of the retry loop as expected
    assert fake_source.download_object_range_as_stream.call_count == 1

    fake_source_err = MagicMock()
    fake_source_err.download_object_range_as_stream.side_effect = Exception("boom")

    # Speed up our test, don't wait for the sleep
    with patch("event_routing_backends.management.commands.transform_tracking_logs.sleep"):
        with pytest.raises(Exception) as e:
            _get_chunks(fake_source_err, "", 0, 1)

    # Make sure we're getting the error we expect
    assert "boom" in str(e)

    # Make sure we got the correct number of retries
    assert fake_source_err.download_object_range_as_stream.call_count == 3
