"""
A generic HTTP Client.
"""
from logging import getLogger

import requests

logger = getLogger(__name__)


class HttpClient:
    """
    A generic HTTP Client.
    """
    def __init__(self, url='', auth_scheme='', auth_key='', headers=None, **options):
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

    def get_auth_header(self):
        """
        Generate auth headers depending upon the client configurations.

        Returns:
            dict
        """
        if self.AUTH_SCHEME:
            return {
                'Authorization': f'{self.AUTH_SCHEME} {self.AUTH_KEY}'
            }
        return {}

    def send(self, json):
        """
        Send the event to configured remote.

        Arguments:
            json (dict) :   event payload to send to host.

        Returns:
            requests.Response object
        """
        headers = self.HEADERS.copy()
        headers.update(self.get_auth_header())

        options = self.options.copy()
        options.update({
            'url': self.URL,
            'json': json,
            'headers': headers,
        })

        logger.debug('Sending event json to {}'.format(self.URL))
        return requests.post(**options)
