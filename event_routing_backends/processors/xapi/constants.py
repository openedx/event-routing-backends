"""
Constants for xAPI specifications.
"""

# xAPI verbs
XAPI_VERB_ATTEMPTED = 'http://adlnet.gov/expapi/verbs/attempted'
XAPI_VERB_ANSWERED = 'http://adlnet.gov/expapi/verbs/answered'
XAPI_VERB_LAUNCHED = 'http://adlnet.gov/expapi/verbs/launched'
XAPI_VERB_REGISTERED = 'http://adlnet.gov/expapi/verbs/registered'
XAPI_VERB_UNREGISTERED = 'http://id.tincanapi.com/verb/unregistered'
XAPI_VERB_COMPLETED = 'http://adlnet.gov/expapi/verbs/completed'
XAPI_VERB_EXPERIENCED = 'http://adlnet.gov/expapi/verbs/experienced'

XAPI_VERB_TERMINATED = 'http://adlnet.gov/expapi/verbs/terminated'
XAPI_VERB_ASKED = 'http://adlnet.gov/expapi/verbs/asked'


XAPI_VERB_INITIALIZED = 'http://adlnet.gov/expapi/verbs/initialized'
XAPI_VERB_PLAYED = 'https://w3id.org/xapi/video/verbs/played'
XAPI_VERB_PAUSED = 'https://w3id.org/xapi/video/verbs/paused'
XAPI_VERB_SEEKED = 'https://w3id.org/xapi/video/verbs/seeked'
XAPI_VERB_INTERACTED = 'http://adlnet.gov/expapi/verbs/interacted'

# xAPI activities
XAPI_ACTIVITY_QUESTION = 'http://adlnet.gov/expapi/activities/question'
XAPI_ACTIVITY_INTERACTION = 'http://adlnet.gov/expapi/activities/interaction'
XAPI_ACTIVITY_COURSE = 'http://adlnet.gov/expapi/activities/course'
XAPI_ACTIVITY_MODULE = 'http://adlnet.gov/expapi/activities/module'
XAPI_ACTIVITY_VIDEO = 'https://w3id.org/xapi/video/activity-type/video'
XAPI_ACTIVITY_LINK = 'http://adlnet.gov/expapi/activities/link'
XAPI_ACTIVITY_POSITION = 'http://id.tincanapi.com/extension/position'

# xAPI context
XAPI_CONTEXT_VIDEO_LENGTH = 'https://w3id.org/xapi/video/extensions/length'
XAPI_CONTEXT_VIDEO_CC_LANGUAGE = 'https://w3id.org/xapi/video/extensions/cc-subtitle-lang'
XAPI_CONTEXT_STARTING_POSITION = 'http://id.tincanapi.com/extension/starting-position'
XAPI_CONTEXT_ENDING_POSITION = 'http://id.tincanapi.com/extension/ending-point'
XAPI_CONTEXT_COMPLETION_THRESHOLD = 'https://w3id.org/xapi/video/extensions/completion-threshold'

# xAPI result
XAPI_RESULT_VIDEO_TIME = 'https://w3id.org/xapi/video/extensions/time'
XAPI_RESULT_VIDEO_TIME_FROM = 'https://w3id.org/xapi/video/extensions/time-from'
XAPI_RESULT_VIDEO_TIME_TO = 'https://w3id.org/xapi/video/extensions/time-to'
XAPI_RESULT_VIDEO_CC_ENABLED = 'https://w3id.org/xapi/video/extensions/cc-enabled'
XAPI_RESULT_VIDEO_PROGRESS = 'https://w3id.org/xapi/video/extensions/progress'
XAPI_TRANSFORMER_VERSION = '1.0.3'

# Languages
EN = 'en'

# Display Names
EXPERIENCED = 'experienced'
INITIALIZED = 'initialized'
REGISTERED = 'registered'
UNREGISTERED = 'unregistered'
ATTEMPTED = 'attempted'
ANSWERED = 'answered'
INTERACTED = 'interacted'
PLAYED = 'played'
PAUSED = 'paused'
COMPLETED = 'completed'
SEEKED = 'seeked'

TERMINATED = 'terminated'
ASKED = 'asked'

# Open edX
OPENEDX_OAUTH2_TOKEN_URL = '/oauth2/access_token'
BLOCK_OBJECT_ID_FORMAT = '{platform}/xblock/{block_usage_key}'
ENROLLMENT_API_URL_FORMAT = '/api/enrollment/v1/enrollment/{username},{course_id}'
