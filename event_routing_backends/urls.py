"""
URLs for event_routing_backends.
"""
from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'', TemplateView.as_view(template_name="event_routing_backends/base.html")),
]
