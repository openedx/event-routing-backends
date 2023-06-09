"""
Class to handle batching and sending bulk transformed statements.
"""
import datetime
import json
import os
from io import BytesIO
from time import sleep

from event_routing_backends.backends.events_router import EventsRouter
from event_routing_backends.management.commands.helpers.event_log_parser import parse_json_event
from event_routing_backends.models import RouterConfiguration
from event_routing_backends.processors.caliper.transformer_processor import CaliperProcessor
from event_routing_backends.processors.xapi.transformer_processor import XApiProcessor


class QueuedSender:
    """
    Handles queuing and sending events to the destination.
    """
    def __init__(
        self,
        destination,
        destination_container,
        destination_prefix,
        transformer_type,
        max_queue_size=10000,
        sleep_between_batches_secs=1.0,
        dry_run=False
    ):
        self.destination = destination
        self.destination_container = destination_container
        self.destination_prefix = destination_prefix
        self.transformer_type = transformer_type
        self.event_queue = []
        self.max_queue_size = max_queue_size
        self.sleep_between_batches = sleep_between_batches_secs
        self.dry_run = dry_run

        # Bookkeeping
        self.queued_lines = 0
        self.skipped_lines = 0
        self.unparsable_lines = 0
        self.batches_sent = 0

        if self.transformer_type == "xapi":
            self.router = EventsRouter(
                backend_name=RouterConfiguration.XAPI_BACKEND,
                processors=[XApiProcessor()]
            )
        else:
            self.router = EventsRouter(
                backend_name=RouterConfiguration.CALIPER_BACKEND,
                processors=[CaliperProcessor()]
            )

    def is_known_event(self, event):
        """
        Check whether any processor cares about this event.
        """
        if "name" in event:
            for processor in self.router.processors:
                if event["name"] in processor.registry.mapping:
                    return True
        return False

    def transform_and_queue(self, line):
        """
        Queue the JSON representation of this log line, if valid and known to any processor.
        """
        event = parse_json_event(line)

        if not event:
            self.unparsable_lines += 1
            return

        if not self.is_known_event(event):
            self.skipped_lines += 1
            return

        self.queue(event)
        self.queued_lines += 1

    def queue(self, event):
        """
        Add an event to the queue, try to send if we've reached our batch size.
        """
        self.event_queue.append(event)
        if len(self.event_queue) == self.max_queue_size:
            if self.dry_run:
                print("Dry run, skipping, but still clearing the queue.")
            else:
                print(f"Max queue size of {self.max_queue_size} reached, sending.")
                if self.destination == "LRS":
                    self.send()
                else:
                    self.store()

                self.batches_sent += 1
            self.event_queue.clear()
            sleep(self.sleep_between_batches)

    def send(self):
        """
        Send to the LRS if we're configured for that, otherwise a no-op.

        Events are converted to the output xAPI / Caliper format in the router.
        """
        if self.destination == "LRS":
            print(f"Sending {len(self.event_queue)} events to LRS...")
            self.router.bulk_send(self.event_queue)
        else:
            print("Skipping send, we're storing with libcloud instead of an LRS.")

    def store(self):
        """
        Store to a libcloud destination if we're configured for that.

        Events are converted to the output xAPI / Caliper format here before being saved.
        """
        if self.destination == "LRS":
            print("Store is being called on an LRS destination, skipping.")
            return

        display_path = os.path.join(self.destination_container, self.destination_prefix.lstrip("/"))
        print(f"Storing {len(self.event_queue)} events to libcloud destination {display_path}")

        container = self.destination.get_container(self.destination_container)

        datestr = datetime.datetime.now().strftime('%y-%m-%d_%H-%M-%S')
        object_name = f"{self.destination_prefix}/{datestr}_{self.transformer_type}.log"
        print(f"Writing to {self.destination_container}/{object_name}")

        out = BytesIO()
        for event in self.event_queue:
            transformed_event = self.router.processors[0](event)
            out.write(str.encode(json.dumps(transformed_event)))
            out.write(str.encode("\n"))
        out.seek(0)

        self.destination.upload_object_via_stream(
            out,
            container,
            object_name
        )

    def finalize(self):
        """
        Send a last batch of events via the LRS, or store a complete set of events to a libcloud destination.
        """
        print(f"Finalizing {len(self.event_queue)} events to {self.destination}")
        if not self.queued_lines:
            print("Nothing in the queue to store!")
        elif self.dry_run:
            print("Dry run, skipping final storage.")
        else:
            # One final send, in case there are events left in the queue
            if self.destination is None or self.destination == "LRS":
                print("Sending to LRS!")
                self.send()
            else:
                print("Storing via Libcloud!")
                self.store()
            self.batches_sent += 1

        print(f"Queued {self.queued_lines} log lines, "
              f"could not parse {self.unparsable_lines} log lines, "
              f"skipped {self.skipped_lines} log lines, "
              f"sent {self.batches_sent} batches.")
