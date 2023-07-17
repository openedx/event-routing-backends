"""
Contains Admin class(es) for the django app.
"""
from config_models.admin import KeyedConfigurationModelAdmin
from django.contrib import admin

from event_routing_backends.models import RouterConfiguration


@admin.register(RouterConfiguration)
class RouterConfigurationAdmin(KeyedConfigurationModelAdmin):
    """
    Admin model class for RouterConfiguration model.
    """

    history_list_display = 'status'
    change_form_template = 'admin/router_conf_change_form.html'

    def get_displayable_field_names(self):
        """
        Get the list display.
        """
        return ['backend_name', 'enabled', 'route_url', 'configurations']
