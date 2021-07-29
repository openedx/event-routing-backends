List of supported edx events
============================

edX events supported by `event-routing-backends` are listed below. Each entry has a link to documentation of that event. Documentation of course completion event will be added soon.

Enrollment events
-----------------

* `edx.course.enrollment.activated`_
* `edx.course.enrollment.deactivated`_

Problem interaction events
---------------------------

* `edx.grades.problem.submitted`_
* `problem_check`_
* `showanswer`_
* `edx.problem.hint.demandhint_displayed`_

Video events
-------------

* `edx.video.loaded`_
* `edx.video.played`_
* `edx.video.stopped`_
* `edx.video.paused`_
* `edx.video.position.changed`_

Course navigation events
------------------------

* `edx.ui.lms.sequence.outline.selected`_
* `edx.ui.lms.sequence.next_selected`_
* `edx.ui.lms.sequence.previous_selected`_
* `edx.ui.lms.sequence.tab_selected`_
* `edx.ui.lms.link_clicked`_

Course completion event
-----------------------

* edx.course.completed


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
