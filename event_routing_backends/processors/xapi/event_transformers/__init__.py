"""
All xAPI transformers.
"""

from event_routing_backends.processors.xapi.event_transformers.enrollment_events import (
    EnrollmentActivatedTransformer,
    EnrollmentDeactivatedTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.navigation_events import (
    LinkClickedTransformer,
    OutlineSelectedTransformer,
    TabNavigationTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.problem_interaction_events import (
    ProblemCheckTransformer,
    ProblemEventsTransformer,
    ProblemSubmittedTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.video_events import (
    VideoCompletedTransformer,
    VideoInteractionTransformers,
    VideoLoadedTransformer,
    VideoPositionChangedTransformer,
)
