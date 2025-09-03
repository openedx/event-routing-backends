Caliper Mapping
###############

edx.course.enrollment.activated
===============================

=================== ============================================
Caliper Key         Value
=================== ============================================
type                Event
Action              Activated
``Actor``
id                  <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                Person
``Object``
id                  <LMS_ROOT_URL>/course/<data [ course_id ]>
type                CourseOffering
name                <name of course-run>
extensions [ mode ] <data [ mode ]>
=================== ============================================

edx.course.enrollment.deactivated
=================================

=================== ============================================
Caliper Key         Value
=================== ============================================
type                Event
Action              Deactivated
``Actor``
id                  <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                Person
``Object``
id                  <LMS_ROOT_URL>/course/<data [ course_id ]>
type                CourseOffering
name                <name of course-run>
extensions [ mode ] <data [ mode ]>
=================== ============================================

edx.course.grade.passed.first_time
==================================

=========== ============================================
Caliper Key Value
=========== ============================================
type        Event
Action      Completed
``Actor``
id          <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type        Person
``Object``
id          <LMS_ROOT_URL>/course/<data [ course_id ]>
type        CourseOffering
name        <name of course-run>
=========== ============================================

problem_check.event_source.server
====================================

================================ ====================================================================================================
Caliper Key                      Value
================================ ====================================================================================================
type                             GradeEvent
Action                           Graded
``Actor``
id                               <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                             Person
``Object``
id                               <LMS_ROOT_URL>/xblock/<data [ problem_id ]> /user/<external_id[ CALIPER ]>/attempt/data [ attempts ]
type                             Attempt
assignee [ id ]                  <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
assignee [ type ]                Person
assignable [ id ]                <LMS_ROOT_URL>/xblock/<data [ problem_id ]>
assignable [ type ]              Assessment
count                            data [ attempts ]
extensions [ isPartOf [ id ] ]   <LMS_ROOT_URL>/course/<data [ course_id ]>
extensions [ isPartOf [ type ] ] CourseOffering
``Generated``
score [ id ]                     _:score
score [ type ]                   Score
score [ maxScore ]                <data [ max_grade ] >
score [ scoreGiven ]             < data [ grade ] >
score [ attempt ]                < data [ attempts ] >
score [ extensions [ success ] ] TRUE if < data [success] >  == "correct" else FALSE
================================ ====================================================================================================

problem_check.event_source.browser
=====================================

=============== ============================================
Caliper Key     Value
=============== ============================================
type            AssessmentEvent
Action          Submitted
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/<data [ problem_id ]>
type            Assessment
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
=============== ============================================

showanswer
==========

================================ ====================================================
Caliper Key                      Value
================================ ====================================================
type                             Event
Action                           Viewed
``Actor``
id                               <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                             Person
``Object``
id                               <LMS_ROOT_URL>/xblock/<data [ problem_id ]>/solution
type                             Annotation
name                             Solution
extensions [ isPartOf [ id ] ]   <LMS_ROOT_URL>/course/<data [ course_id ]>
extensions [ isPartOf [ type ] ] CourseOffering
================================ ====================================================

edx.problem.hint.demandhint_displayed
=====================================

================================ ========================================================================
Caliper Key                      Value
================================ ========================================================================
type                             Event
Action                           Viewed
``Actor``
id                               <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                             Person
``Object``
id                               <LMS_ROOT_URL>/xblock/<data [ problem_id ]>/hint/ <data [ hint_index ] >
type                             Annotation
name                             Hint
extensions [ isPartOf [ id ] ]   <LMS_ROOT_URL>/course/<data [ course_id ]>
extensions [ isPartOf [ type ] ] CourseOffering
================================ ========================================================================

edx.video.loaded
================

=============== ========================================================================================================
Caliper Key     Value
=============== ========================================================================================================
type            MediaEvent
Action          Started
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type            VideoObject
duration        data [ duration ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
=============== ========================================================================================================

edx.video.played
================

=============== ========================================================================================================
Caliper Key     Value
=============== ========================================================================================================
type            MediaEvent
Action          Resumed
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type            VideoObject
duration        data [ duration ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
``Target``
currentTime     data [ currentTime ]
id              _:MediaLocation
type            MediaLocation
=============== ========================================================================================================

edx.video.stopped
=================

=============== ========================================================================================================
Caliper Key     Value
=============== ========================================================================================================
type            MediaEvent
Action          Ended
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type            VideoObject
duration        data [ duration ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
``Target``
currentTime     data [ currentTime ]
id              _:MediaLocation
type            MediaLocation
=============== ========================================================================================================

edx.video.paused
================

=============== ========================================================================================================
Caliper Key     Value
=============== ========================================================================================================
type            MediaEvent
Action          Paused
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type            VideoObject
duration        data [ duration ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
``Target``
currentTime     data [ currentTime ]
id              _:MediaLocation
type            MediaLocation
=============== ========================================================================================================

edx.video.position.changed
==========================

==================== ========================================================================================================
Caliper Key          Value
==================== ========================================================================================================
type                 MediaEvent
Action               JumpedTo
``Actor``
id                   <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                 Person
``Object``
id                   <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                 VideoObject
duration             data [ duration ]
isPartOf [id]        <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]      CourseOffering
``Target``
currentTime          data [ old_time ]
id                   _:MediaLocation
type                 MediaLocation
extensions [newTime] data [ new_time ]
==================== ========================================================================================================

complete_video
==============

=============== ========================================================================================================
Caliper Key     Value
=============== ========================================================================================================
type            Event
Action          Completed
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type            VideoObject
duration        data [ duration ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
=============== ========================================================================================================

edx.video.closed_captions.shown
===============================

==================== ========================================================================================================
Caliper Key          Value
==================== ========================================================================================================
type                 MediaEvent
Action               EnabledClosedCaptioning
``Actor``
id                   <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                 Person
``Object``
id                   <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                 VideoObject
duration             data [ duration ]
isPartOf [id]        <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]      CourseOffering
``Target``
currentTime          data [ current_time ]
id                   _:MediaLocation
type                 MediaLocation
==================== ========================================================================================================

edx.video.closed_captions.hidden
================================

==================== ========================================================================================================
Caliper Key          Value
==================== ========================================================================================================
type                 MediaEvent
Action               DisabledClosedCaptioning
``Actor``
id                   <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                 Person
``Object``
id                   <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                 VideoObject
duration             data [ duration ]
isPartOf [id]        <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]      CourseOffering
``Target``
currentTime          data [ current_time ]
id                   _:MediaLocation
type                 MediaLocation
==================== ========================================================================================================

edx.video.transcript.shown
==========================

==================== ========================================================================================================
Caliper Key          Value
==================== ========================================================================================================
type                 MediaEvent
Action               EnabledClosedCaptioning
``Actor``
id                   <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                 Person
``Object``
id                   <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                 VideoObject
duration             data [ duration ]
isPartOf [id]        <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]      CourseOffering
``Target``
currentTime          data [ current_time ]
id                   _:MediaLocation
type                 MediaLocation
==================== ========================================================================================================

edx.video.transcript.hidden
===========================

==================== ========================================================================================================
Caliper Key          Value
==================== ========================================================================================================
type                 MediaEvent
Action               DisabledClosedCaptioning
``Actor``
id                   <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                 Person
``Object``
id                   <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                 VideoObject
duration             data [ duration ]
isPartOf [id]        <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]      CourseOffering
``Target``
currentTime          data [ current_time ]
id                   _:MediaLocation
type                 MediaLocation
==================== ========================================================================================================

speed_change_video
==================

====================== ========================================================================================================
Caliper Key            Value
====================== ========================================================================================================
type                   MediaEvent
Action                 ChangedSpeed
``Actor``
id                     <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                   Person
``Object``
id                     <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
type                   VideoObject
duration               data [ duration ]
isPartOf [id]          <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]        CourseOffering
``Target``
currentTime            data [ current_time ]
id                     _:MediaLocation
type                   MediaLocation
extensions [oldSpeed]   data [ old_speed ]
extensions [newSpeed]   data [ new_speed ]
====================== ========================================================================================================

edx.ui.lms.sequence.outline.selected
====================================

=============== ============================================
Caliper Key     Value
=============== ============================================
type            NavigationEvent
Action          NavigatedTo
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              data [ target_url ]
type            DigitalResource
name            data [ target_name ]
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
=============== ============================================

edx.ui.lms.sequence.next_selected
=================================

========================== ============================================
Caliper Key                Value
========================== ============================================
type                       NavigationEvent
Action                     NavigatedTo
``Actor``
id                         <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                       Person
``Object``
id                         <LMS_ROOT_URL>/xblock/<data [ id ]>
type                       DigitalResourceCollection
name                       Unit
isPartOf [id]              <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]            CourseOffering
extensions [ target ]      "next unit"
extensions [ current_tab ] data [current_tab]
extensions [ tab_count ]   data [ tab_count ]
========================== ============================================

edx.ui.lms.sequence.previous_selected
=====================================

========================== ============================================
Caliper Key                Value
========================== ============================================
type                       NavigationEvent
Action                     NavigatedTo
``Actor``
id                         <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                       Person
``Object``
id                         <LMS_ROOT_URL>/xblock/<data [ id ]>
type                       DigitalResourceCollection
name                       Unit
isPartOf [id]              <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]            CourseOffering
extensions [ target ]      "previous unit"
extensions [ current_tab ] data [current_tab]
extensions [ tab_count ]   data [ tab_count ]
========================== ============================================

edx.ui.lms.sequence.tab_selected
================================

========================== ============================================
Caliper Key                Value
========================== ============================================
type                       NavigationEvent
Action                     NavigatedTo
``Actor``
id                         <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type                       Person
``Object``
id                         <LMS_ROOT_URL>/xblock/<data [ id ]>
type                       DigitalResourceCollection
name                       Unit
isPartOf [id]              <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type]            CourseOffering
extensions [ target ]      data [ target_tab ]
extensions [ current_tab ] data [current_tab]
extensions [ tab_count ]   data [ tab_count ]
========================== ============================================

edx.ui.lms.link_clicked
=======================

=============== ============================================
Caliper Key     Value
=============== ============================================
type            NavigationEvent
Action          NavigatedTo
``Actor``
id              <LMS_ROOT_URL>/user/<external_id[ CALIPER ]>
type            Person
``Object``
id              data [ target_url ]
type            Webpage
isPartOf [id]   <LMS_ROOT_URL>/course/<data [ course_id ]>
isPartOf [type] CourseOffering
=============== ============================================
