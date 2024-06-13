"""
Helper utilities for event transformer settings.
"""

from typing import List


def event_tracking_backends_config(settings, allowed_xapi_events: List[str], allowed_caliper_events: List[str]) -> dict:
    """
    Return the recommended settings.EVENT_TRACKING_BACKENDS configuration.

    Include the given `allowed_xapi_events` and `allowed_caliper_events` in the relevant backend whitelists.
    """
    all_allowed_events = set(allowed_xapi_events + allowed_caliper_events)

    return {
        'event_transformer': {
            'ENGINE': 'eventtracking.backends.async_routing.AsyncRoutingBackend',
            'OPTIONS': {
                'backend_name': 'event_transformer',
                'processors': [
                    {
                        'ENGINE': 'eventtracking.processors.whitelist.NameWhitelistProcessor',
                        'OPTIONS': {
                            'whitelist': all_allowed_events
                        }
                    },
                ],
                'backends': {
                    'xapi': {
                        'ENGINE': 'event_routing_backends.backends.async_events_router.AsyncEventsRouter',
                        'OPTIONS': {
                            'processors': [
                                {
                                    'ENGINE': 'eventtracking.processors.whitelist.NameWhitelistProcessor',
                                    'OPTIONS': {
                                        'whitelist': allowed_xapi_events
                                    }
                                },
                                {
                                    'ENGINE':
                                        'event_routing_backends.processors.xapi.transformer_processor.XApiProcessor',
                                    'OPTIONS': {}
                                }
                            ],
                            'backend_name': 'xapi',
                        }
                    },
                    "caliper": {
                        'ENGINE': 'event_routing_backends.backends.async_events_router.AsyncEventsRouter',
                        "OPTIONS": {
                            "processors": [
                                {
                                    "ENGINE": "eventtracking.processors.whitelist.NameWhitelistProcessor",
                                    "OPTIONS": {
                                        "whitelist": allowed_caliper_events
                                    }
                                },
                                {
                                    "ENGINE":
                                        "event_routing_backends.processors."
                                        "caliper.transformer_processor.CaliperProcessor",
                                    "OPTIONS": {}
                                },
                                {
                                    "ENGINE":
                                        "event_routing_backends.processors."
                                        "caliper.envelope_processor.CaliperEnvelopeProcessor",
                                    "OPTIONS": {
                                        "sensor_id": settings.LMS_ROOT_URL
                                    }
                                }
                            ],
                            "backend_name": "caliper"
                        }
                    }
                },
            },
        }
    }
