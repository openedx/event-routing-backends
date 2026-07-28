"""
All xAPI transformers.
"""

from event_routing_backends.processors.xapi.event_transformers.completion_events import CompletionCreatedTransformer
from event_routing_backends.processors.xapi.event_transformers.enrollment_events import (
    EnrollmentActivatedTransformer,
    EnrollmentDeactivatedTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.exam_events import (
    PracticeExamCreatedTransformer,
    PracticeExamSubmittedTransformer,
    ProctoredExamCreatedTransformer,
    ProctoredExamSubmittedTransformer,
    TimedExamCreatedTransformer,
    TimedExamSubmittedTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.forum_events import (
    ThreadCreatedTransformer,
    ThreadDeletedTransformer,
    ThreadEditedTransformer,
    ThreadResponseCreatedTransformer,
    ThreadResponseReportedTransformer,
    ThreadResponseUnReportedTransformer,
    ThreadViewedTransformer,
    ThreadVotedTransformer,
)
from event_routing_backends.processors.xapi.event_transformers.grading_events import (
    CourseGradedTransformer,
    SubsectionGradedTransformer,
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
    VideoCCTransformers,
    VideoCompletedTransformer,
    VideoInteractionTransformers,
    VideoLoadedTransformer,
    VideoPositionChangedTransformer,
    VideoSpeedChangedTransformer,
)
