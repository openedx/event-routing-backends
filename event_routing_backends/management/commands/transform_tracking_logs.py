"""
Management command for transforming tracking log files.
"""
import json
import os
from io import BytesIO
from textwrap import dedent
from time import sleep

from django.conf import settings
from django.core.management.base import BaseCommand
from libcloud.storage.providers import get_driver
from libcloud.storage.types import Provider

from event_routing_backends.management.commands.helpers.queued_sender import QueuedSender

# Number of bytes to download at a time, this is 2 MB
CHUNK_SIZE = 1024 * 1024 * 2


def _get_chunks(source, file, start_byte, end_byte):
    """
    Fetch a chunk from the upstream source, retry 3 times if necessary.

    Often an upstream provider like S3 will fail occasionally on big jobs. This
    tries to handle any of those cases gracefully.
    """
    chunks = None
    num_retries = getattr(settings, 'EVENT_ROUTING_BACKEND_BULK_DOWNLOAD_MAX_RETRIES', 3)
    retry_countdown = getattr(settings, 'EVENT_ROUTING_BACKEND_BULK_DOWNLOAD_COUNTDOWN', 1)

    # Skipping coverage here because it wants to test a branch that will never
    # be hit (for -> return)
    for try_number in range(1, num_retries+1):  # pragma: no cover
        try:
            chunks = source.download_object_range_as_stream(
                file,
                start_bytes=start_byte,
                end_bytes=end_byte
            )
            break
        # Catching all exceptions here because there's no telling what all
        # the possible errors from different libcloud providers are.
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(e)
            if try_number == num_retries:
                print(f"Try {try_number}: Error occurred downloading, giving up.")
                raise
            print(f"Try {try_number}: Error occurred downloading source file chunk. Trying again in 1 second.")
            sleep(retry_countdown)

    return chunks


def transform_tracking_logs(
    source,
    source_container,
    source_prefix,
    sender
):
    """
    Transform one or more tracking log files from the given source to the given destination.
    """
    # Containers are effectively directories, this recursively tries to find files
    # matching the given prefix in the given source.
    container = source.get_container(container_name=source_container)

    display_path = os.path.join(source_container, source_prefix.lstrip("/"))
    print(f"Looking for log files in {display_path}*")

    for file in source.iterate_container_objects(container, source_prefix):
        # Download the file as a stream of characters to save on memory
        print(f"Streaming file {file}...")

        last_successful_byte = 0
        line = ""

        while last_successful_byte < int(file.size):
            end_byte = last_successful_byte + CHUNK_SIZE

            if end_byte > file.size:
                end_byte = file.size

            chunks = _get_chunks(source, file, last_successful_byte, end_byte)

            for chunk in chunks:
                chunk = chunk.decode('utf-8')

                # Loop through this chunk, if we find a newline it's time to process
                # otherwise just keep appending.
                for char in chunk:
                    if char == "\n" and line:
                        sender.transform_and_queue(line)
                        line = ""
                    else:
                        line += char

            last_successful_byte = end_byte
        # Sometimes the file doesn't end with a newline, we try to use
        # any remaining bytes as a final line.
        if line:
            sender.transform_and_queue(line)  # pragma: no cover

    # Give the queue a chance to send any remaining events left in the queue
    sender.finalize()


def get_source_config_from_options(source_config_options):
    """
    Prepare our source configuration from the configuration JSON.
    """
    source_config = json.loads(source_config_options)
    try:
        source_prefix = source_config.pop("prefix")
        source_container = source_config.pop("container")
        return source_config, source_container, source_prefix
    except KeyError as e:
        print("The following keys must be defined in source_config: 'prefix', 'container'")
        raise e


def get_dest_config_from_options(destination_provider, dest_config_options):
    """
    Prepare our destination configuration.

    All None's if these are being sent to an LRS, or use values from the destination_configuration JSON option.
    """
    if destination_provider != "LRS":
        dest_config = json.loads(dest_config_options)
        try:
            dest_container = dest_config.pop("container")
            dest_prefix = dest_config.pop("prefix")
        except KeyError as e:
            print("If not using the 'LRS' destination, the following keys must be defined in "
                  "destination_config: 'prefix', 'container'")
            raise e
    else:
        dest_config = dest_container = dest_prefix = None

    return dest_config, dest_container, dest_prefix


def validate_source_and_files(driver, container_name, prefix):
    """
    Validate that the given libcloud source exists and has files in it to read.
    """
    container = driver.get_container(container_name)
    objects = list(driver.iterate_container_objects(container, prefix))
    if not objects:
        raise FileNotFoundError(f"No files found in {container_name}/{prefix}*")
    print(f"Found {len(objects)} files in {container_name}/{prefix}*")
    return [f"{obj.name} - {obj.size} bytes" for obj in objects]


def validate_destination(driver, container_name, prefix, source_objects):
    """
    Validate that the given libcloud destination exists and can be written to.
    """
    container = driver.get_container(container_name)
    full_path = f"{prefix}/manifest.log"
    file_list = "\n".join(source_objects)
    driver.upload_object_via_stream(
        iterator=BytesIO(file_list.encode()),
        container=container,
        object_name=full_path
    )
    print(f"Wrote source file list to '{container_name}/{full_path}'")


def get_libcloud_drivers(source_provider, source_config, destination_provider, destination_config):
    """
    Attempt to configure the libcloud drivers for source and destination.
    """
    try:
        source_provider = getattr(Provider, source_provider)
        source_cls = get_driver(source_provider)
        source_driver = source_cls(**source_config)
    except AttributeError:
        print(f"{source_provider} is not a valid source Libcloud provider.")
        raise

    # There is no driver for LRS
    destination_driver = "LRS"
    if destination_provider != "LRS":
        try:
            destination_provider = getattr(Provider, destination_provider)
            destination_cls = get_driver(destination_provider)
            destination_driver = destination_cls(**destination_config)
        except AttributeError:
            print(f"{destination_provider} is not a valid destination Libcloud provider.")
            raise

    return source_driver, destination_driver


class Command(BaseCommand):
    """
    Transform tracking logs to an LRS or other output destination.
    """
    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument(
            '--source_provider',
            type=str,
            help="An Apache Libcloud 'provider constant' from: "
                 "https://libcloud.readthedocs.io/en/stable/storage/supported_providers.html . "
                 "Ex: LOCAL for local storage or S3 for AWS S3.",
            required=True,
        )
        parser.add_argument(
            '--source_config',
            type=str,
            help="A JSON dictionary of configuration for the source provider. Leave"
                 "blank the destination_provider is 'LRS'. See the Libcloud docs for the necessary options"
                 "for your destination. If your destination (S3, MinIO, etc) needs a 'bucket' or 'container' add them "
                 "to the config here under the key 'container'. If your source needs a prefix (ex: directory path, "
                 "or wildcard beginning of a filename), add it here under the key 'prefix'. If no prefix is given, "
                 "all files in the given location will be attempted!",
            required=True,
        )
        parser.add_argument(
            '--destination_provider',
            type=str,
            default="LRS",
            help="Either 'LRS' to use the default configured xAPI and/or Caliper servers"
                 "or an Apache Libcloud 'provider constant' from this list: "
                 "https://libcloud.readthedocs.io/en/stable/storage/supported_providers.html . "
                 "Ex: LOCAL for local storage or S3 for AWS S3.",
        )
        parser.add_argument(
            '--destination_config',
            type=str,
            help="A JSON dictionary of configuration for the destination provider. Not needed for the 'LRS' "
                 "destination_provider. See the Libcloud docs for the necessary options for your destination. If your "
                 "destination (S3, MinIO, etc) needs a 'bucket' or 'container' add them to the config here under the "
                 "key 'container'. If your destination needs a prefix (ex: directory path), add it here under the key "
                 "'prefix'. If no prefix is given, the output file(s) will be written to the base path.",
        )
        parser.add_argument(
            '--transformer_type',
            choices=["xapi", "caliper"],
            required=True,
            help="The type of transformation to do, only one can be done at a time.",
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=10000,
            help="How many events to send at a time. For the LRS destination this will be one POST per this many "
                 "events, for all other destinations a new file will be created containing up to this many events. "
                 "This helps reduce memory usage in the script and increases helps with LRS performance.",
        )
        parser.add_argument(
            '--sleep_between_batches_secs',
            type=float,
            default=10.0,
            help="Fractional seconds to sleep between sending batches to a destination, used to reduce load on the LMS "
                 "and LRSs when performing large operations.",
        )
        parser.add_argument(
            '--dry_run',
            action="store_true",
            help="Attempt to transform all lines from all files, but do not send to the destination.",
        )

    def handle(self, *args, **options):
        """
        Configure the command and start the transform process.
        """
        source_config, source_container, source_prefix = get_source_config_from_options(options["source_config"])
        dest_config, dest_container, dest_prefix = get_dest_config_from_options(
            options["destination_provider"],
            options["destination_config"]
        )

        source_driver, dest_driver = get_libcloud_drivers(
            options["source_provider"],
            source_config,
            options["destination_provider"],
            dest_config
        )

        source_file_list = validate_source_and_files(source_driver, source_container, source_prefix)
        if dest_driver != "LRS":
            validate_destination(dest_driver, dest_container, dest_prefix, source_file_list)
        else:
            print(f"Found {len(source_file_list)} source files: ", *source_file_list, sep="\n")

        sender = QueuedSender(
            dest_driver,
            dest_container,
            dest_prefix,
            options["transformer_type"],
            max_queue_size=options["batch_size"],
            sleep_between_batches_secs=options["sleep_between_batches_secs"],
            dry_run=options["dry_run"]
        )

        transform_tracking_logs(
            source_driver,
            source_container,
            source_prefix,
            sender
        )
