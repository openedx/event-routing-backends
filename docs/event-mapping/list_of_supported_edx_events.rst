List of supported edx events
============================

edX events supported by `event-routing-backends` are listed below. Each entry has a link to documentation of that event. Documentation of course completion event will be added soon.

Enrollment events
-----------------

* `edx.course.enrollment.activated`
* `edx.course.enrollment.deactivated`

Problem interaction events
---------------------------

* `edx.grades.problem.submitted`
* `problem_check`
* `showanswer`
* `edx.problem.hint.demandhint_displayed`

Video events
-------------

* `edx.video.loaded`
* `edx.video.played`
* `edx.video.stopped`
* `edx.video.paused`
* `edx.video.position.changed`

Course navigation events
------------------------

* `edx.ui.lms.sequence.outline.selected`
* `edx.ui.lms.sequence.next_selected`
* `edx.ui.lms.sequence.previous_selected`
* `edx.ui.lms.sequence.tab_selected`
* `edx.ui.lms.link_clicked`

Course completion event
-----------------------

* edx.course.completed


.. `edx.course.enrollment.activated`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-course-enrollment-activated-and-edx-course-enrollment-deactivated
.. `edx.course.enrollment.deactivated`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-course-enrollment-activated-and-edx-course-enrollment-deactivated
.. `edx.grades.problem.submitted`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/course_team_event_types.html#edx-grades-problem-submitted
.. `problem_check`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#problem-check
.. `showanswer`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#showanswer
.. `edx.problem.hint.demandhint_displayed`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-problem-hint-demandhint-displayed
.. `edx.video.loaded`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#load-video-edx-video-loaded
.. `edx.video.played`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#play-video-edx-video-played
.. `edx.video.stopped`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#stop-video-edx-video-stopped
.. `edx.video.paused`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#pause-video-edx-video-paused
.. `edx.video.position.changed`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#seek-video-edx-video-position-changed
.. `edx.ui.lms.sequence.outline.selected`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-outline-selected
.. `edx.ui.lms.sequence.next_selected`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#example-edx-ui-lms-sequence-next-selected-events
.. `edx.ui.lms.sequence.previous_selected`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-sequence-previous-selected
.. `edx.ui.lms.sequence.tab_selected`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-sequence-tab-selected
.. `edx.ui.lms.link_clicked`: http://edx.readthedocs.io/projects/devdata/en/latest/internal_data_formats/tracking_logs/student_event_types.html#edx-ui-lms-link-clicked

