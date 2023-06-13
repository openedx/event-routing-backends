"""
Production settings for the event_routing_backends app.
"""


def plugin_settings(settings):
    """
    Override the default event_routing_backends app settings with production settings.
    """
    settings.EVENT_ROUTING_BACKEND_MAX_RETRIES = settings.ENV_TOKENS.get(
        'EVENT_ROUTING_BACKEND_MAX_RETRIES',
        settings.EVENT_ROUTING_BACKEND_MAX_RETRIES
    )
    settings.EVENT_ROUTING_BACKEND_COUNTDOWN = settings.ENV_TOKENS.get(
        'EVENT_ROUTING_BACKEND_COUNTDOWN',
        settings.EVENT_ROUTING_BACKEND_COUNTDOWN
    )
    settings.CALIPER_EVENTS_ENABLED = settings.ENV_TOKENS.get(
        'CALIPER_EVENTS_ENABLED',
        settings.CALIPER_EVENTS_ENABLED
    )
    settings.CALIPER_EVENT_LOGGING_ENABLED = settings.ENV_TOKENS.get(
        'CALIPER_EVENT_LOGGING_ENABLED',
        settings.CALIPER_EVENT_LOGGING_ENABLED
    )
    settings.XAPI_EVENTS_ENABLED = settings.ENV_TOKENS.get(
        'XAPI_EVENTS_ENABLED',
        settings.XAPI_EVENTS_ENABLED
    )
    settings.XAPI_EVENT_LOGGING_ENABLED = settings.ENV_TOKENS.get(
        'XAPI_EVENT_LOGGING_ENABLED',
        settings.XAPI_EVENT_LOGGING_ENABLED
    )
    settings.EVENT_TRACKING_BACKENDS = settings.ENV_TOKENS.get(
        'EVENT_TRACKING_BACKENDS',
        settings.EVENT_TRACKING_BACKENDS
    )
    settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS = settings.ENV_TOKENS.get(
        'EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS',
        settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS
    )
    settings.XAPI_AGENT_IFI_TYPE = settings.ENV_TOKENS.get(
        'XAPI_AGENT_IFI_TYPE',
        settings.XAPI_AGENT_IFI_TYPE
    )
