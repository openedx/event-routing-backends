
edx.course.enrollment.activated
===============================

=========================================================================== ==========================================
xAPI Key                                                                    Value
=========================================================================== ==========================================
``Actor``
objectType                                                                  Agent
account [ homePage ]                                                        <LMS_ROOT_URL>
account [ name ]                                                            <anonymized-user-id>
``Verb``
id                                                                          http://adlnet.gov/expapi/verbs/registered
display [ en-US ]                                                           registered
``Object``
id                                                                          <LMS_ROOT_URL>/course/<data [ course_id ]>
objectType                                                                  Activity
definition [ type ]                                                         http://adlnet.gov/expapi/activities/course
definition [ name ][ en-US ]                                                <name of course-run>
definition [ extensions [ https://w3id.org/xapi/acrossx/extensions/type ] ] <data [ mode ]>
=========================================================================== ==========================================

edx.course.enrollment.deactivated
=================================

=========================================================================== ==========================================
xAPI Key                                                                    Value
=========================================================================== ==========================================
``Actor``
objectType                                                                  Agent
account [ homePage ]                                                        <LMS_ROOT_URL>
account [ name ]                                                            <anonymized-user-id>
``Verb``
id                                                                          http://id.tincanapi.com/verb/unregistered
display [ en-US ]                                                           unregistered
``Object``
id                                                                          <LMS_ROOT_URL>/course/<data [ course_id ]>
objectType                                                                  Activity
definition [ type ]                                                         http://adlnet.gov/expapi/activities/course
definition [ name ][ en-US ]                                                <name of course-run>
definition [ extensions [ https://w3id.org/xapi/acrossx/extensions/type ] ] <data [ mode ]>
=========================================================================== ==========================================

edx.course.grade.passed.first_time
==================================

============================ ==========================================
xAPI Key                     Value
============================ ==========================================
``Actor``
objectType                   Agent
account [ homePage ]         <LMS_ROOT_URL>
account [ name ]             <anonymized-user-id>
``Verb``
id                           http://adlnet.gov/expapi/verbs/passed
display [ en-US ]            passed
``Object``
id                           <LMS_ROOT_URL>/course/<data [ course_id ]>
definition [ type ]          http://adlnet.gov/expapi/activities/course
definition [ name ][ en-US ] <name of course-run>
============================ ==========================================

edx.problem.hint.demandhint_displayed
=====================================

============================================================= ============================================================
xAPI Key                                                      Value
============================================================= ============================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            http://adlnet.gov/expapi/verbs/asked
display [ en-US ]                                             asked
``Object``
id                                                            <LMS_ROOT_URL>/xblock/<data [ module_id ]>/hint/<hint_index>
objectType                                                    Activity
definition [ type ]                                           https://w3id.org/xapi/acrossx/extensions/supplemental-info
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
============================================================= ============================================================

edx.ui.lms.link_clicked
=======================

============================================================= =============================================
xAPI Key                                                      Value
============================================================= =============================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            https://w3id.org/xapi/dod-isd/verbs/navigated
display [ en-US ]                                             Navigated
``Object``
id                                                            <data [ target_url ]>
objectType                                                    Activity
definition [ type ]                                           http://adlnet.gov/expapi/activities/link
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
============================================================= =============================================

edx.ui.lms.sequence.next_selected
=================================

================================================================================== =============================================
xAPI Key                                                                           Value
================================================================================== =============================================
``Actor``
objectType                                                                         Agent
account [ homePage ]                                                               <LMS_ROOT_URL>
account [ name ]                                                                   <anonymized-user-id>
``Verb``
id                                                                                 https://w3id.org/xapi/dod-isd/verbs/navigated
display [ en-US ]                                                                  Navigated
``Object``
id                                                                                 <LMS_ROOT_URL>/xblock/<data [ id ]>
objectType                                                                         Activity
definition [ type ]                                                                http://id.tincanapi.com/activitytype/resource
definition [ extensions [ https://w3id.org/xapi/acrossx/extensions/total-items ] ] <data [ tab_count ]>
``Context``
contextActivities [ parent [ objectType ] ]                                        Activity
contextActivities [ parent [ id ] ]                                                <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]                               http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]                      <name of course-run>
extensions [ http://id.tincanapi.com/extension/s
tarting-point ]                   data [current_tab]
extensions [ http://http://id.tincanapi.com/extension/ending-point ]               "next unit"
================================================================================== =============================================

edx.ui.lms.sequence.outline.selected
====================================

============================================================= =============================================
xAPI Key                                                      Value
============================================================= =============================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            https://w3id.org/xapi/dod-isd/verbs/navigated
display [ en-US ]                                             Navigated
``Object``
id                                                            <data [ target_url ]>
objectType                                                    Activity
definition [ type ]                                           http://adlnet.gov/expapi/activities/module
definition [ name ][ en-US ]                                  <data [ target_name ]>
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
============================================================= =============================================

edx.ui.lms.sequence.previous_selected
=====================================

================================================================================== =============================================
xAPI Key                                                                           Value
================================================================================== =============================================
``Actor``
objectType                                                                         Agent
account [ homePage ]                                                               <LMS_ROOT_URL>
account [ name ]                                                                   <anonymized-user-id>
``Verb``
id                                                                                 https://w3id.org/xapi/dod-isd/verbs/navigated
display [ en-US ]                                                                  Navigated
``Object``
id                                                                                 <LMS_ROOT_URL>/xblock/<data [ id ]>
objectType                                                                         Activity
definition [ type ]                                                                http://id.tincanapi.com/activitytype/resource
definition [ extensions [ https://w3id.org/xapi/acrossx/extensions/total-items ] ] <data [ tab_count ]>
``Context``
contextActivities [ parent [ objectType ] ]                                        Activity
contextActivities [ parent [ id ] ]                                                <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]                               http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]                      <name of course-run>
extensions [ http://id.tincanapi.com/extension/s
tarting-point ]                   data [current_tab]
extensions [ http://http://id.tincanapi.com/extension/ending-point ]               "previous unit"
================================================================================== =============================================

edx.ui.lms.sequence.tab_selected
================================

================================================================================== =============================================
xAPI Key                                                                           Value
================================================================================== =============================================
``Actor``
objectType                                                                         Agent
account [ homePage ]                                                               <LMS_ROOT_URL>
account [ name ]                                                                   <anonymized-user-id>
``Verb``
id                                                                                 https://w3id.org/xapi/dod-isd/verbs/navigated
display [ en-US ]                                                                  Navigated
``Object``
id                                                                                 <LMS_ROOT_URL>/xblock/<data [ id ]>
objectType                                                                         Activity
definition [ type ]                                                                http://id.tincanapi.com/activitytype/resource
definition [ extensions [ https://w3id.org/xapi/acrossx/extensions/total-items ] ] <data [ tab_count ]>
``Context``
contextActivities [ parent [ objectType ] ]                                        Activity
contextActivities [ parent [ id ] ]                                                <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]                               http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]                      <name of course-run>
extensions [ http://id.tincanapi.com/extension/s
tarting-point ]                   data [current_tab]
extensions [ http://http://id.tincanapi.com/extension/ending-point ]               <data [ target_tab ]>
================================================================================== =============================================

edx.video.loaded
================

============================================================= ========================================================================================================
xAPI Key                                                      Value
============================================================= ========================================================================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            http://adlnet.gov/expapi/verbs/initialized
display [ en-US ]                                             initialized
``Object``
id                                                            <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                    Activity
definition [ type ]                                           https://w3id.org/xapi/video/activity-type/video
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]  <data [ duration ]>
============================================================= ========================================================================================================

edx.video.paused
================

============================================================= ========================================================================================================
xAPI Key                                                      Value
============================================================= ========================================================================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            https://w3id.org/xapi/video/verbs/paused
display [ en-US ]                                             paused
``Object``
id                                                            <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                    Activity
definition [ type ]                                           https://w3id.org/xapi/video/activity-type/video
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]  <data [ duration ]>
``Result``
extensions [ https://w3id.org/xapi/video/extensions/time ]    <data [ currentTime ]>
============================================================= ========================================================================================================

edx.video.played
================

============================================================= ========================================================================================================
xAPI Key                                                      Value
============================================================= ========================================================================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            https://w3id.org/xapi/video/verbs/played
display [ en-US ]                                             played
``Object``
id                                                            <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                    Activity
definition [ type ]                                           https://w3id.org/xapi/video/activity-type/video
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]  <data [ duration ]>
============================================================= ========================================================================================================

edx.video.position.changed
==========================

=============================================================== ========================================================================================================
xAPI Key                                                        Value
=============================================================== ========================================================================================================
``Actor``
objectType                                                      Agent
account [ homePage ]                                            <LMS_ROOT_URL>
account [ name ]                                                <anonymized-user-id>
``Verb``
id                                                              https://w3id.org/xapi/video/verbs/seeked
display [ en-US ]                                               seeked
``Object``
id                                                              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                      Activity
definition [ type ]                                             https://w3id.org/xapi/video/activity-type/video
``Context``
contextActivities [ parent [ objectType ] ]                     Activity
contextActivities [ parent [ id ] ]                             <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]            http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]   <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]    <data [ duration ]>
``Result``
extensions [ https://w3id.org/xapi/video/extensions/time-from ] <data [ old_time ]>
extensions [ https://w3id.org/xapi/video/extensions/time-to ]   <data [ new_time ]>
=============================================================== ========================================================================================================

edx.video.stopped
==================

============================================================= ========================================================================================================
xAPI Key                                                      Value
============================================================= ========================================================================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            http://adlnet.gov/expapi/verbs/terminated
display [ en-US ]                                             terminated
``Object``
id                                                            <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                    Activity
definition [ type ]                                           https://w3id.org/xapi/video/activity-type/video
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]  <data [ duration ]>
``Result``
extensions [ https://w3id.org/xapi/video/extensions/time ]    <data [ currentTime ]>
============================================================= ========================================================================================================

problem_check (event_source: browser)
=====================================

============================================================= =================================================================================================================
xAPI Key                                                      Value
============================================================= =================================================================================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            http://adlnet.gov/expapi/verbs/attempted
display [ en-US ]                                             attempted
``Object``
id                                                            <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@problem+block@<block_id from data>
objectType                                                    Activity
definition [ type ]                                           http://adlnet.gov/expapi/activities/cmi.interaction
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
============================================================= =================================================================================================================

problem_check (event_source: server)
=====================================

========================================================================== ======================================================================================================
xAPI Key                                                                   Value
========================================================================== ======================================================================================================
``Actor``
objectType                                                                 Agent
account [ homePage ]                                                       <LMS_ROOT_URL>
account [ name ]                                                           <anonymized-user-id>
``Verb``
id                                                                         https://w3id.org/xapi/acrossx/verbs/evaluated
display [ en-US ]                                                          evaluated
``Object``
id                                                                         <LMS_ROOT_URL>/xblock/<data [ problem_id ]>
objectType                                                                 Activity
definition [ type ]                                                        http://adlnet.gov/expapi/activities/cmi.interaction
definition [description]                                                   <data [ submission ] [ 0 ] [ question ]> if <[ submission ] [ 0 ] [ response_type ]> is not empty
definition [ interactionType ]                                             Mapping of <data [submission] [ 0 ] [response_type]> if <[ submission ] [ 0 ] [ response_type ]> is not empty
definition [ extensions [ http://id.tincanapi.com/extension/attempt-id ] ] <data [attempts]>
``Context``
contextActivities [ parent [ objectType ] ]                                Activity
contextActivities [ parent [ id ] ]                                        <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]                       http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]              <name of course-run>
``Results``
success                                                                    TRUE if <data [success]>  == "correct" else FALSE
score [ min ]                                                              0
score [ max ]                                                              <data [max_grade]>
score [ raw ]                                                              <data [grade]>
score [ scaled ]                                                           <data [grade]> / <data [max_grade]>
response                                                                   <data [submission] [ 0 ] [answer]> if <[ submission ] [ 0 ] [ response_type ]> is not empty
========================================================================== ======================================================================================================

Mapping of ``response_type`` to ``interactionType``:

====================== ===============
response_type          interactionType
====================== ===============
choiceresponse         choice
multiplechoiceresponse choice
numericalresponse      numeric
stringresponse         fill-in
customresponse         other
coderesponse           other
externalresponse       other
formularesponse        fill-in
schematicresponse      other
imageresponse          matching
annotationresponse     fill-in
choicetextresponse     choice
optionresponse         choice
symbolicresponse       fill-in
truefalseresponse      true-false
====================== ===============

showanswer
==========

============================================================= ==================================================
xAPI Key                                                      Value
============================================================= ==================================================
``Actor``
objectType                                                    Agent
account [ homePage ]                                          <LMS_ROOT_URL>
account [ name ]                                              <anonymized-user-id>
``Verb``
id                                                            http://adlnet.gov/expapi/verbs/asked
display [ en-US ]                                             asked
``Object``
id                                                            <LMS_ROOT_URL>/xblock/<data [ problem_id ]>/answer
objectType                                                    Activity
definition [ type ]                                           http://id.tincanapi.com/activitytype/solution
``Context``
contextActivities [ parent [ objectType ] ]                   Activity
contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
============================================================= ==================================================
