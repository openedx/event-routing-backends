"""
Contains Admin class(es) for the django app.
"""
from config_models.admin import KeyedConfigurationModelAdmin
from django.contrib import admin

from event_routing_backends.models import RouterConfiguration


class RouterConfigurationAdmin(KeyedConfigurationModelAdmin):
    """
    Admin model class for RouterConfiguration model.
    """

    list_display = ('backend_name', 'is_enabled', 'configurations',)
    history_list_display = ('status')


admin.site.register(RouterConfiguration, RouterConfigurationAdmin)
