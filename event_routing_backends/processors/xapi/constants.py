"""
Constants for xAPI specifications.
"""

# xAPI verbs
XAPI_VERB_ATTEMPTED = 'http://adlnet.gov/expapi/verbs/attempted'
XAPI_VERB_EVALUATED = 'https://w3id.org/xapi/acrossx/verbs/evaluated'
XAPI_VERB_ANSWERED = 'http://adlnet.gov/expapi/verbs/answered'
XAPI_VERB_LAUNCHED = 'http://adlnet.gov/expapi/verbs/launched'
XAPI_VERB_REGISTERED = 'http://adlnet.gov/expapi/verbs/registered'
XAPI_VERB_UNREGISTERED = 'http://id.tincanapi.com/verb/unregistered'
XAPI_VERB_COMPLETED = 'http://adlnet.gov/expapi/verbs/completed'
XAPI_VERB_PASSED = 'http://adlnet.gov/expapi/verbs/passed'
XAPI_VERB_FAILED = 'http://adlnet.gov/expapi/verbs/failed'
XAPI_VERB_EXPERIENCED = 'http://adlnet.gov/expapi/verbs/experienced'
XAPI_VERB_NAVIGATED = 'https://w3id.org/xapi/dod-isd/verbs/navigated'
XAPI_VERB_POSTED = 'https://w3id.org/xapi/acrossx/verbs/posted'
XAPI_VERB_EDITED = 'https://w3id.org/xapi/acrossx/verbs/edited'
XAPI_VERB_VIEWED = 'http://id.tincanapi.com/verb/viewed'
XAPI_VERB_DELETED = 'https://w3id.org/xapi/dod-isd/verbs/deleted'
XAPI_VERB_VOTED = 'https://w3id.org/xapi/openedx/verb/voted'
XAPI_VERB_REPORTED = 'https://w3id.org/xapi/acrossx/verbs/reported'
XAPI_VERB_UNREPORTED = 'https://w3id.org/xapi/openedx/verb/unreported'
XAPI_VERB_EARNED = 'http://id.tincanapi.com/verb/earned'

XAPI_VERB_PROGRESSED = 'http://adlnet.gov/expapi/verbs/progressed'
XAPI_VERB_TERMINATED = 'http://adlnet.gov/expapi/verbs/terminated'
XAPI_VERB_ASKED = 'http://adlnet.gov/expapi/verbs/asked'


XAPI_VERB_INITIALIZED = 'http://adlnet.gov/expapi/verbs/initialized'
XAPI_VERB_PLAYED = 'https://w3id.org/xapi/video/verbs/played'
XAPI_VERB_PAUSED = 'https://w3id.org/xapi/video/verbs/paused'
XAPI_VERB_SEEKED = 'https://w3id.org/xapi/video/verbs/seeked'
XAPI_VERB_INTERACTED = 'http://adlnet.gov/expapi/verbs/interacted'

# xAPI activities
XAPI_ACTIVITY_QUESTION = 'http://adlnet.gov/expapi/activities/question'
XAPI_ACTIVITY_SOLUTION = 'http://id.tincanapi.com/activitytype/solution'
XAPI_ACTIVITY_RESOURCE = 'http://id.tincanapi.com/activitytype/resource'
XAPI_ACTIVITY_INTERACTION = 'http://adlnet.gov/expapi/activities/cmi.interaction'
XAPI_ACTIVITY_SUPPLEMENTAL_INFO = 'https://w3id.org/xapi/acrossx/extensions/supplemental-info'
XAPI_ACTIVITY_COURSE = 'http://adlnet.gov/expapi/activities/course'
XAPI_ACTIVITY_MODULE = 'http://adlnet.gov/expapi/activities/module'
XAPI_ACTIVITY_VIDEO = 'https://w3id.org/xapi/video/activity-type/video'
XAPI_ACTIVITY_DISCUSSION = 'http://id.tincanapi.com/activitytype/discussion'
XAPI_ACTIVITY_LINK = 'http://adlnet.gov/expapi/activities/link'
XAPI_ACTIVITY_POSITION = 'http://id.tincanapi.com/extension/position'
XAPI_ACTIVITY_TOTAL_COUNT = 'https://w3id.org/xapi/acrossx/extensions/total-items'
XAPI_ACTIVITY_MODE = 'https://w3id.org/xapi/acrossx/extensions/type'
XAPI_ACTIVITY_ATTEMPT = 'http://id.tincanapi.com/extension/attempt-id'
XAPI_ACTIVITY_GRADE_CLASSIFICATION = 'http://www.tincanapi.co.uk/activitytypes/grade_classification'
XAPI_ACTIVITY_GRADE = 'http://www.tincanapi.co.uk/extensions/result/classification'
XAPI_ACTIVITY_TIMED_ASSESSMENT = 'https://w3id.org/xapi/openedx/activity/timed-assessment'
XAPI_ACTIVITY_PRACTICE_ASSESSMENT = 'https://w3id.org/xapi/openedx/activity/practice-assessment'
XAPI_ACTIVITY_PROCTORED_ASSESSMENT = 'https://w3id.org/xapi/openedx/activity/proctored-assessment'
XAPI_ACTIVITY_PROGRESS = 'https://w3id.org/xapi/cmi5/result/extensions/progress'

# xAPI context
XAPI_CONTEXT_VIDEO_LENGTH = 'https://w3id.org/xapi/video/extensions/length'
XAPI_CONTEXT_VIDEO_CC_LANGUAGE = 'https://w3id.org/xapi/video/extensions/cc-subtitle-lang'
XAPI_CONTEXT_STARTING_POSITION = 'http://id.tincanapi.com/extension/starting-position'
XAPI_CONTEXT_ENDING_POSITION = 'http://id.tincanapi.com/extension/ending-point'
XAPI_CONTEXT_COMPLETION_THRESHOLD = 'https://w3id.org/xapi/video/extensions/completion-threshold'
XAPI_CONTEXT_SESSION_ID = 'https://w3id.org/xapi/openedx/extensions/session-id'

XAPI_ACTIVITY_TIME_LIMIT = 'https://w3id.org/xapi/acrossx/extensions/time-limit'

XAPI_ACTIVITY_EXAM_ATTEMPT = 'http://adlnet.gov/expapi/activities/attempt'

XAPI_CONTEXT_ATTEMPT_STARTED = 'https://w3id.org/xapi/openedx/extension/attempt-started'
XAPI_CONTEXT_ATTEMPT_COMPLETED = 'https://w3id.org/xapi/openedx/extension/attempt-completed'
XAPI_CONTEXT_DURATION = 'http://id.tincanapi.com/extension/duration'
XAPI_CONTEXT_CODE = 'https://w3id.org/xapi/openedx/extension/code'

# xAPI result
XAPI_RESULT_VIDEO_TIME = 'https://w3id.org/xapi/video/extensions/time'
XAPI_RESULT_VIDEO_TIME_FROM = 'https://w3id.org/xapi/video/extensions/time-from'
XAPI_RESULT_VIDEO_TIME_TO = 'https://w3id.org/xapi/video/extensions/time-to'
XAPI_RESULT_VIDEO_SPEED_FROM = 'https://w3id.org/xapi/openedx/extension/speed-from'
XAPI_RESULT_VIDEO_SPEED_TO = 'https://w3id.org/xapi/openedx/extension/speed-to'
XAPI_RESULT_VIDEO_CC_ENABLED = 'https://w3id.org/xapi/video/extensions/cc-enabled'
XAPI_RESULT_VIDEO_PROGRESS = 'https://w3id.org/xapi/video/extensions/progress'
# Every request from a Client and every response from the LRS includes an HTTP header
# with the name X-Experience-API-Version and the version as the value. This parameter contains
# xAPI specification version of the statements being pushed or pulled from LRS
# https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-About.md#Appendix1A
XAPI_SPECIFICATION_VERSION = '1.0.3'
XAPI_TRANSFORMER_VERSION_KEY = 'https://w3id.org/xapi/openedx/extension/transformer-version'

# Languages
EN = 'en'
EN_US = 'en-US'

# Display Names
EXPERIENCED = 'experienced'
INITIALIZED = 'initialized'
REGISTERED = 'registered'
UNREGISTERED = 'unregistered'
ATTEMPTED = 'attempted'
EVALUATED = 'evaluated'
ANSWERED = 'answered'
INTERACTED = 'interacted'
PLAYED = 'played'
PAUSED = 'paused'
COMPLETED = 'completed'
PASSED = 'passed'
FAILED = 'failed'
SEEKED = 'seeked'
POSTED = 'posted'
VIEWED = 'viewed'
DELETED = 'deleted'
EDITED = 'edited'
VOTED = 'voted'
REPORTED = 'reported'
UNREPORTED = 'unreported'
EARNED = 'earned'
PROGRESSED = 'progressed'

TERMINATED = 'terminated'
NAVIGATED = 'navigated'
ASKED = 'asked'

# Open edX
OPENEDX_OAUTH2_TOKEN_URL = '/oauth2/access_token'
BLOCK_OBJECT_ID_FORMAT = '{platform}/xblock/{block_usage_key}'
ENROLLMENT_API_URL_FORMAT = '/api/enrollment/v1/enrollment/{username},{course_id}'
