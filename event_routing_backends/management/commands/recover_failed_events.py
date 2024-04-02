"""
Management command for resending events when a failure occurs.
"""

import logging
from textwrap import dedent

from django.conf import settings
from django.core.management.base import BaseCommand
from eventtracking.tracker import get_tracker

from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command for resending events when a failure occurs
    in the event routing backend.
    """

    help = dedent(__doc__).strip()

    def add_arguments(self, parser):
        parser.add_argument(
            "--transformer_type",
            choices=["xapi", "caliper"],
            required=True,
            help="The type of transformed events to recover.",
        )
        parser.add_argument(
            "--batch_size",
            default=100,
            help="The number of events to recover at a time. Default is 100.",
        )

    def handle(self, *args, **options):
        """
        Configure the command and start the transform process.
        """
        logger.info("Recovering failed events")
        logger.warning("This command is intended for use in recovery situations only.")
        transformer_type = options["transformer_type"]
        batch_size = options["batch_size"]
        tracker = get_tracker()

        engine = tracker.backends["event_transformer"]
        backend = engine.backends[transformer_type]

        # In the recovery process we are disabling batching to prevent
        # single event failures from blocking the recovery process.
        settings.EVENT_ROUTING_BACKEND_BATCHING_ENABLED = False

        success = 0
        malformed = 0
        failed = 0

        while failed_events := backend.get_failed_events(batch_size):
            logger.info(
                "Recovering {} failed events for backend {}".format(
                    len(failed_events), transformer_type
                )
            )
            for event in failed_events:
                try:
                    backend.send(event)
                    success += 1
                except EventNotDispatched:
                    logger.error("Malformed event: {}".format(event["name"]))
                    malformed += 1
                except Exception as e:  # pylint: disable=broad-except
                    # Backend can still be in a bad state, so we need to catch all exceptions
                    logger.error("Failed to send event: {}".format(e))
                    failed += 1

        logger.info("Recovery process completed.")
        logger.info("Recovered events  : {}".format(success))
        logger.info("Failed to recover : {}".format(failed))
        logger.info("Malformed events  : {} ".format(malformed))
