"""
Management command for resending events when a failure occurs.
"""

import logging
from textwrap import dedent

from django.conf import settings
from django.core.management.base import BaseCommand
from eventtracking.backends.event_bus import EventBusRoutingBackend
from eventtracking.tracker import get_tracker

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
            choices=["xapi", "caliper", "all"],
            required=True,
            help="The type of transformation to do, only one can be done at a time.",
        )

    def handle(self, *args, **options):
        """
        Configure the command and start the transform process.
        """
        logger.info("Recovering failed events")
        transformer_type = options["transformer_type"]
        tracker = get_tracker()

        engines = {
            name: engine
            for name, engine in tracker.backends.items()
            if isinstance(engine, EventBusRoutingBackend)
        }

        if not engines:
            logger.info("No compatible backend found.")
            return

        settings.EVENT_ROUTING_BACKEND_BATCHING_ENABLED = False

        for name, engine in engines.items():
            if transformer_type not in ("all", name):
                logger.info("Skipping backend: {}".format(name))
                continue
            for backend_name, backend in engine.backends.items():
                failed_events = backend.get_failed_events()
                if not failed_events:
                    logger.info(
                        "No failed events found for backend: {}".format(backend_name)
                    )
                    continue
                for event in failed_events:
                    backend.send(event)
