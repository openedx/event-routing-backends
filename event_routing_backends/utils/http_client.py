"""
A generic HTTP Client.
"""
from logging import getLogger

import requests

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched

logger = getLogger(__name__)


class HttpClient:
    """
    A generic HTTP Client.
    """

    def __init__(self, url='', auth_scheme='', auth_key='', headers=None, username=None, password=None, **options):
        """
        Initialize the client with provided configurations.

        This client supports any paramters that can be passed to `requests.post` call.
        https://requests.readthedocs.io/en/latest/api/

        url (str)        :     URL for the event consumer.
        auth_scheme (str) :     Scheme used for authentication.
        auth_key (str)    :     API key used in the authorization header.
        headers (str)     :     Any additional headers to be sent with event payload.
        """
        self.URL = url
        self.AUTH_SCHEME = auth_scheme
        self.AUTH_KEY = auth_key
        self.HEADERS = headers or {}
        self.options = options
        self.username = username
        self.password = password

    def get_auth_header(self):
        """
        Generate auth headers depending upon the client configurations.

        Returns:
            dict
        """
        if self.AUTH_SCHEME == RouterConfiguration.AUTH_BEARER:
            return {
                'Authorization': f'{self.AUTH_SCHEME} {self.AUTH_KEY}'
            }
        return {}

    def bulk_send(self, events):
        """
        Send the list of events to a configured remote.

        Arguments:
            events (list[dict]) :   list of event payloads to send to host.

        Returns:
            requests.Response object
        """
        headers = self.HEADERS.copy()
        headers.update(self.get_auth_header())

        options = self.options.copy()
        options.update({
            'url': self.URL,
            'json': events,
            'headers': headers,
        })
        if self.AUTH_SCHEME == RouterConfiguration.AUTH_BASIC:
            options.update({'auth': (self.username, self.password)})
        logger.debug('Sending caliper version of {} edx events to {}'.format(len(events), self.URL))
        response = requests.post(**options)   # pylint: disable=missing-timeout

        if not 200 <= response.status_code < 300:
            logger.warning(
                '{} request failed for sending Caliper version of {} edx events to {}.Response code: {}. '
                'Response: '
                '{}'.format(
                    response.request.method,
                    len(events), self.URL,
                    response.status_code,
                    response.text
                ))
            raise EventNotDispatched

    def send(self, event, event_name):
        """
        Send the event to configured remote.

        Arguments:
            event (dict)        :   event payload to send to host.
            event_name (str)    :   name of the original event.

        Returns:
            requests.Response object
        """
        headers = self.HEADERS.copy()
        headers.update(self.get_auth_header())

        options = self.options.copy()
        options.update({
            'url': self.URL,
            'json': event,
            'headers': headers,
        })
        if self.AUTH_SCHEME == RouterConfiguration.AUTH_BASIC:
            options.update({'auth': (self.username, self.password)})
        logger.debug('Sending caliper version of edx event "{}" to {}'.format(event_name, self.URL))
        response = requests.post(**options)   # pylint: disable=missing-timeout

        if not 200 <= response.status_code < 300:
            logger.warning(
                '{} request failed for sending Caliper version of edx event "{}" to {}.Response code: {}. Response: '
                '{}'.format(
                    response.request.method,
                    event_name, self.URL,
                    response.status_code,
                    response.text
                ))
            raise EventNotDispatched
