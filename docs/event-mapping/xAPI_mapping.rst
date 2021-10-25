========== ============================================================= ==================================================
showanswer
========== ============================================================= ==================================================
Actor
           objectType                                                    Agent
           account [ homePage ]                                          <LMS_ROOT_URL>
           account [ name ]                                              <anonymized-user-id>
Verb
           id                                                            http://adlnet.gov/expapi/verbs/asked
           display [ en-US ]                                             asked
Object
           id                                                            <LMS_ROOT_URL>/xblock/<data [ problem_id ]>/answer
           objectType                                                    Activity
           definition [ type ]                                           http://id.tincanapi.com/activitytype/solution
Context
           contextActivities [ parent [ objectType ] ]                   Activity
           contextActivities [ parent [ id ] ]                           <LMS_ROOT_URL>/course/<data [ course_id ]>
           contextActivities [ parent [ definition [ type ] ] ]          http://adlnet.gov/expapi/activities/course
           contextActivities [ parent [ definition [ name ][ en-US ] ] ] <name of course-run>
========== ============================================================= ==================================================
