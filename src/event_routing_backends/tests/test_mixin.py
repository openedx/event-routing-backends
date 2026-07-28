"""
Mixin for testing transformers for all of the currently supported events
"""
from event_routing_backends.tests.factories import RouterConfigurationFactory


class RouterTestMixin:
    """
    Test `Router` Mixin
    """

    def create_router_configuration(self, config_fixture, backend_name='first'):
        """
        Return RouterConfigurationFactory object for given configurations and backend name.

        Arguments:
            config_fixture    (dict):     router configurations dictionary
            backend_name       (str):     Backend names like caliper/xapi

        Returns:
            obj(RouterConfigurationFactory)
        """

        return RouterConfigurationFactory(
            configurations=config_fixture,
            enabled=True,
            route_url='http://test2.com',
            backend_name=backend_name
        )
