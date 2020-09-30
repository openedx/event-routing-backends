"""
Database models for event_routing_backends.
"""
from config_models.models import ConfigurationModel
from django.db import models

from event_routing_backends.utils.fields import EncryptedJSONField


def get_value_from_dotted_path(dict_obj, dotted_key):
    """
    Map the dotted key to nested keys for dict and return the matching value.

    For example:
        'key_a.key_b.key_c' will look for the folowing value:

        {
            'key_a': {
                'key_b': {
                    'key_c': 'final value'
                }
            }
        }

    Arguments:
        dict_obj (dict)  :    dictionary for which the value is required
        dotted_key (str) :    dotted key string for the dict

    Returns:
        ANY :                 Returns the value found in the dict or `None` if
                              no value exists for provided dotted path.
    """
    nested_keys = dotted_key.split('.')
    result = dict_obj
    try:
        for key in nested_keys:
            result = result[key]
    except KeyError:
        return None
    return result


class RouterConfiguration(ConfigurationModel):
    """
    Configurations for filtering and then routing events to hosts.

    An example of how the configuration would look like is as follows:

    ```
    [
        {
            'router_type': 'AUTH_HEADERS',
            'match_params': {
                'data.key': 'value'
            },
            'host_configurations': {
                'url': 'http://test1.com',
                'headers': {},
                'auth_scheme': 'Bearer',
                'auth_key': 'test_key'
            },
            'override_args': {
                'new_key': 'new_value'
            }
        },
        {
            'router_type': 'LRS_CLIENT',
            'match_params': {
                'data.key': 'value'
            },
            'host_configurations': {
                'url': 'http://test1.com',
            },
        },
    ]
    ```

    Any event that is passed to the router, will be compared and tested for
    `match_params` present in every object of `configurations` list. If the event
    passes the test for some configuration, that event will be routed to that host
    as per the `host_configurations`.

    .. no_pii:

    """

    KEY_FIELDS = ('backend_name',)
    backend_name = models.CharField(
        max_length=50,
        verbose_name='Backend name',
        null=False,
        blank=False,
        help_text=(
            'Name of the tracking backend on which this router should be applied.'
            '<br/>'
            'Please note that this field is <b>case sensitive.</b>'
        )
    )

    configurations = EncryptedJSONField()

    class Meta:
        """
        Meta class.
        """

        verbose_name = 'Router Configuration'
        verbose_name_plural = 'Router Configurations'

    def __str__(self):
        """
        Return string representation for class instance.
        """
        return '{id} - {backend} - {enabled}'.format(
            id=self.pk,
            backend=self.backend_name,
            enabled='Enabled' if self.enabled else 'Disabled'
        )

    @classmethod
    def get_enabled_router(cls, backend_name):
        """
        Return enabled router.

        Return the enabled router for the backend matching the `backend_name`.

        Arguments:
            backend_name (str):     Name of the backend for which the router is required.

        Returns:
            RouterConfiguration or None
        """
        router_config = cls.current(backend_name)
        return router_config if router_config.enabled else None

    def get_allowed_hosts(self, original_event):
        """
        Return list of hosts to which the `transformed_event` is allowed to be sent.

        Every object of `configurations` list may have the `match_params` key:
        ```
        [
            {
                ...
                'match_params': {
                    'data.key': 'value'
                },
                ...
            },
            ...
        ]
        ```

        if `match_params` is found in a hosts' configuration, the dotted paths in
        keys are used to get respective values from the event and are then
        compared with the values present in the configurations. If all values match,
        then the event is allowed to be routed to the host.
        e.g. the configuration mentioned above will let the events of the following
        format to be routed:
        ```
        {
            'data': {
                ...,
                'key': 'value'
            },
            ...
        }
        ```

        Else if no `match_params` is present for some host, the event is allowed
        to be routed to that host by default.

        Arguments:
            original_event    (dict):       original event dict

        Returns
            list<dict>
        """
        allowed_hosts = []
        for host_config in self.configurations:
            is_allowed = self._match_event_for_host(original_event, host_config)

            if is_allowed:
                allowed_hosts.append(host_config)

        return allowed_hosts

    def _match_event_for_host(self, original_event, host_config):
        """
        Return True if the `original_event` matches the `match_params` in `host_config`.

        Arguments:
            original_event    (dict):     original event dict
            host_config       (dict):     host configurations dict

        Returns:
            bool
        """
        for key, value in host_config.get('match_params', {}).items():
            if get_value_from_dotted_path(original_event, key) != value:
                return False
        return True
