.. _filters:

OpenEdx Filters
###############

This is an integration that allows to modify current standard outputs by using the `openedx-filters`_ library and is limited to the following filters per processor:


xAPI Filters
------------

+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| Filter                                                                                          | Description                                                                        |
+=================================================================================================+====================================================================================+
| event_routing_backends.processors.xapi.transformer.xapi_transformer.get_actor                   | Intercepts and allows to modify the xAPI actor field, this affects all xAPI events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.transformer.xapi_transformer.get_verb                    | Intercepts and allows to modify the xAPI actor field, this affects all xAPI events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.completion_events.completion_created.get_object          | Allows to modify the xAPI object field, this just affects completion events        |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.enrollment_events.base_enrollment.get_object             | Allows to modify the xAPI object field, this just affects enrollment events        |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.exam_events.base_exam.get_object                         | Allows to modify the xAPI object field, this just affects exam events              |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.forum_events.base_forum_thread.get_object                | Allows to modify the xAPI object field, this just affects forum events             |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.grading_events.subsection_graded.get_object              | Allows to modify the xAPI object field, this just affects subsection_graded events |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.grading_events.course_graded.get_object                  | Allows to modify the xAPI object field, this just affects course_graded events     |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.link_clicked.get_object                | Allows to modify the xAPI object field, this just affects link_clicked events      |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.outline_selected.get_object            | Allows to modify the xAPI object field, this just affects outline_selected events  |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.navigation_events.tab_navigation.get_object              | Allows to modify the xAPI object field, this just affects tab_navigation events    |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.problem_interaction_events.base_problems.get_object      | Allows to modify the xAPI object field, this just affects problem events           |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.problem_interaction_events.base_problem_check.get_object | Allows to modify the xAPI object field, this just affects problem_check events     |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+
| event_routing_backends.processors.xapi.video_events.base_video.get_object                       | Allows to modify the xAPI object field, this affects all video events              |
+-------------------------------------------------------------------------------------------------+------------------------------------------------------------------------------------+

.. _openedx-filters: https://github.com/openedx/openedx-filters
