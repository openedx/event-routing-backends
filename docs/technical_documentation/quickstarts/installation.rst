Installation
############

Install event routing backends library or add it to private requirements of your virtual environment ( ``requirements/private.txt`` ).

#. Run ``pip install edx-event-routing-backends``.

#. Run migrations ( ``python manage.py lms migrate`` ).

#. Restart LMS service and celery workers of edx-platform.
