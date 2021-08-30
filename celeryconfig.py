from celery import Celery
from django.conf import settings

app = Celery('event_routing_backends')

app.config_from_object(settings)

app.autodiscover_tasks()
task_always_eager = settings.CELERY_ALWAYS_EAGER
