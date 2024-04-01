"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from os.path import abspath, dirname, join

from test_utils import _mock_third_party_modules


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'event_routing_backends',
    'celery_utils',
)

LOCALE_PATHS = [
    root('event_routing_backends', 'conf', 'locale'),
]

SECRET_KEY = 'insecure-secret-key'
LMS_ROOT_URL = 'http://localhost:18000'
CELERY_ALWAYS_EAGER = True
XAPI_EVENTS_ENABLED = True
XAPI_EVENT_LOGGING_ENABLED = False
RUNNING_WITH_TEST_SETTINGS = True
EVENT_TRACKING_BACKENDS = {}
XAPI_AGENT_IFI_TYPE = 'external_id'
EVENT_ROUTING_BACKEND_BATCHING_ENABLED = False
EVENT_ROUTING_BACKEND_BATCH_INTERVAL = 100
EVENT_TRACKING_ENABLED = True
EVENT_TRACKING_BACKENDS = {
    "event_transformer": {
        "ENGINE": "eventtracking.backends.async_routing.AsyncRoutingBackend",
        "OPTIONS": {
            "backends": {
                "xapi": {
                    "ENGINE": "event_routing_backends.backends.async_events_router.AsyncEventsRouter",
                    "OPTIONS": {
                        "processors": [
                            {
                                "ENGINE": "event_routing_backends.processors.xapi.transformer_processor.XApiProcessor",
                                "OPTIONS": {},
                            }
                        ],
                        "backend_name": "xapi",
                    },
                },
                "caliper": {
                    "ENGINE": "event_routing_backends.backends.async_events_router.AsyncEventsRouter",
                    "OPTIONS": {
                        "processors": [
                            {
                                "ENGINE": "event_routing_backends.processors."
                                "caliper.transformer_processor.CaliperProcessor",
                                "OPTIONS": {},
                            },
                        ],
                        "backend_name": "caliper",
                    },
                },
            },
        },
    },
}
_mock_third_party_modules()
