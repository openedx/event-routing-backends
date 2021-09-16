"""
Production settings for the event_routing_backends app.
"""


def plugin_settings(settings):
    """
    Override the default event_routing_backends app settings with production settings.
    """
    config = dict(settings.EVENT_TRACKING_BACKENDS)
    config.update(settings.ENV_TOKENS.get('EVENT_TRACKING_BACKENDS'))
    settings.EVENT_TRACKING_BACKENDS = config
    config_critical_events = list(settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS)
    config_critical_events.update(settings.ENV_TOKENS.get('EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS'))
    settings.EVENT_TRACKING_BACKENDS_BUSINESS_CRITICAL_EVENTS = config_critical_events


