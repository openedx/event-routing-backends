... _supported-events:

List of supported edx events
============================

edX events supported by `event-routing-backends` are listed below.

Enrollment events
-----------------

* `edx.course.enrollment.activated`_
* `edx.course.enrollment.deactivated`_

Problem interaction events
---------------------------

* `problem_check`_ with ``event_source`` as ``server``
* `problem_check`_ with ``event_source`` as ``browser``
* `showanswer`_
* `edx.problem.hint.demandhint_displayed`_

Video events
-------------

* `edx.video.loaded`_ (legacy name: ``load_video``)
* `edx.video.played`_ (legacy name: ``play_video``)
* `edx.video.stopped`_ (legacy name: ``stop_video``)
* `edx.video.paused`_ (legacy name: ``pause_video``)
* `edx.video.position.changed`_ (legacy name: ``seek_video``)


Course navigation events
------------------------

* `edx.ui.lms.sequence.outline.selected`_
* `edx.ui.lms.sequence.next_selected`_
* `edx.ui.lms.sequence.previous_selected`_
* `edx.ui.lms.sequence.tab_selected`_
* `edx.ui.lms.link_clicked`_

Course grading events
-----------------------

* ``edx.course.grade.passed.first_time``

new
===

=============================================================== ======================================================================================================== ======================================== ========================================= ======================================== ========================================
open edX event name                                             edx.video.loaded                                                                                         edx.video.played                         edx.video.stopped                         edx.video.paused                         edx.video.position.changed
=============================================================== ======================================================================================================== ======================================== ========================================= ======================================== ========================================
Actor
objectType                                                      Agent
openid                                                          https://openedx.org/users/user-v1:<anonymized-user-id>
account [ homePage ]                                            <LMS_ROOT_URL>
account [ name ]                                                <anonymized-user-id>
Verb
id                                                              http://adlnet.gov/expapi/verbs/initialized                                                               https://w3id.org/xapi/video/verbs/played http://adlnet.gov/expapi/verbs/terminated https://w3id.org/xapi/video/verbs/paused https://w3id.org/xapi/video/verbs/seeked
display [ en-US ]                                               initialized                                                                                              played                                   terminated                                paused                                   seeked
Object
id                                                              <LMS_ROOT_URL>/xblock/block-v1:<context [ course_id ] minus "course-v1:">+type@video+block@<data [ id ]>
objectType                                                      Activity
definition [ type ]                                             https://w3id.org/xapi/video/activity-type/video
Context
contextActivities [ parent [ objectType ] ]                     Activity
contextActivities [ parent [ id ] ]                             <LMS_ROOT_URL>/course/<data [ course_id ]>
contextActivities [ parent [ definition [ type ] ] ]            http://adlnet.gov/expapi/activities/course
contextActivities [ parent [ definition [ name ][ en-US ] ] ]   <name of course-run>
extensions [ https://w3id.org/xapi/video/extensions/length ]    data [ duration ]
dtype: Float with max 3 decimals
Result
extensions [ https://w3id.org/xapi/video/extensions/time ]      n/a                                                                                                      data [ currentTime ]                     data [ currentTime ]                      data [ currentTime ]                     n/a
extensions [ https://w3id.org/xapi/video/extensions/time-from ] n/a                                                                                                      n/a                                      n/a                                       n/a                                      data [ old_time ]
extensions [ https://w3id.org/xapi/video/extensions/time-to ]   n/a                                                                                                      n/a                                      n/a                                       n/a                                      data [ new_time ]
=============================================================== ======================================================================================================== ======================================== ========================================= ======================================== ========================================


.. _edx.course.enrollment.activated: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-course-enrollment-activated-and-edx-course-enrollment-deactivated
.. _edx.course.enrollment.deactivated: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-course-enrollment-activated-and-edx-course-enrollment-deactivated
.. _edx.grades.problem.submitted: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/course_team_event_types.html#edx-grades-problem-submitted
.. _problem_check: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#problem-check
.. _showanswer: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#showanswer
.. _edx.problem.hint.demandhint_displayed: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-problem-hint-demandhint-displayed
.. _edx.video.loaded: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#load-video-edx-video-loaded
.. _edx.video.played: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#play-video-edx-video-played
.. _edx.video.stopped: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#stop-video-edx-video-stopped
.. _edx.video.paused: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#pause-video-edx-video-paused
.. _edx.video.position.changed: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#seek-video-edx-video-position-changed
.. _edx.ui.lms.sequence.outline.selected: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-outline-selected
.. _edx.ui.lms.sequence.next_selected: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#example-edx-ui-lms-sequence-next-selected-events
.. _edx.ui.lms.sequence.previous_selected: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-sequence-previous-selected
.. _edx.ui.lms.sequence.tab_selected: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-sequence-tab-selected
.. _edx.ui.lms.link_clicked: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-link-clicked
