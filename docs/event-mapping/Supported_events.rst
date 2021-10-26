
List of supported edx events
============================

edX events supported by ``event-routing-backends`` are listed below.

Enrollment events
-----------------

* `edx.course.enrollment.activated`_  | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.course.enrollment.activated.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.course.enrollment.activated.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.course.enrollment.activated.json>`_
* `edx.course.enrollment.deactivated`_ | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.course.enrollment.deactivated.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.course.enrollment.deactivated.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_  , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.course.enrollment.deactivated.json>`_

Problem interaction events
---------------------------
::

   `problem_check`_ with ``event_source`` as ``server``  | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/problem_check(server).json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/problem_check(server).json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/problem_check(server).json>`_

   `problem_check`_ with ``event_source`` as ``browser`` | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/problem_check(browser).json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/problem_check(browser).json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/problem_check(browser).json>`_

   `showanswer`_                                         | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/showanswer.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/showanswer.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/showanswer.json>`_

   `edx.problem.hint.demandhint_displayed`_              | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.problem.hint.demandhint_displayed.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.problem.hint.demandhint_displayed.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.problem.hint.demandhint_displayed.json>`_

Video events
-------------

* `edx.video.loaded`_ (legacy name: ``load_video``) | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/load_video.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/load_video.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/load_video.json>`_
* `edx.video.played`_ (legacy name: ``play_video``) | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/play_video.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/play_video.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/play_video.json>`_
* `edx.video.stopped`_ (legacy name: ``stop_video``) | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/stop_video.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/stop_video.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/stop_video.json>`_
* `edx.video.paused`_ (legacy name: ``pause_video``) | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/pause_video.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/pause_video.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/pause_video.json>`_
* `edx.video.position.changed`_ (legacy name: ``seek_video``) | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/seek_video.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/seek_video.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/seek_video.json>`_


Course navigation events
------------------------

* `edx.ui.lms.sequence.outline.selected`_ | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.ui.lms.sequence.outline.selected.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.ui.lms.sequence.outline.selected.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.ui.lms.sequence.outline.selected.json>`_
* `edx.ui.lms.sequence.next_selected`_  | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.ui.lms.sequence.next_selected.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.ui.lms.sequence.next_selected.json>`_  | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.ui.lms.sequence.next_selected.json>`_
* `edx.ui.lms.sequence.previous_selected`_ | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.ui.lms.sequence.previous_selected.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.ui.lms.sequence.previous_selected.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.ui.lms.sequence.previous_selected.json>`_
* `edx.ui.lms.sequence.tab_selected`_  | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.ui.lms.sequence.tab_selected.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.ui.lms.sequence.tab_selected.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.ui.lms.sequence.tab_selected.json>`_
* `edx.ui.lms.link_clicked`_ | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.ui.lms.link_clicked.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.ui.lms.link_clicked.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.ui.lms.link_clicked.json>`_

Course grading events
-----------------------

* edx.course.grade.passed.first_time | edX `sample <../../event_routing_backends/processors/tests/fixtures/current/edx.course.grade.passed.first_time.json>`_ | xAPI `map <./xAPI_mapping.rst>`_ , `sample <../../event_routing_backends/processors/xapi/tests/fixtures/expected/edx.course.grade.passed.first_time.json>`_ | Caliper `map <https://docs.google.com/spreadsheets/d/1MgHddOO6G33sSpknvYi-aXuLiBmuKTfHmESsXpIiuU8/edit#gid=389163646>`_ , `sample <../../event_routing_backends/processors/caliper/tests/fixtures/expected/edx.course.grade.passed.first_time.json>`_


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
