"""
An LRS client for xAPI stores.
"""
from logging import getLogger

from tincan.remote_lrs import RemoteLRS

from event_routing_backends.models import RouterConfiguration
from event_routing_backends.processors.transformer_utils.exceptions import EventNotDispatched

logger = getLogger(__name__)


class LrsClient:
    """
    An LRS client for xAPI stores.
    """

    def __init__(self, url=None, version=None, auth_scheme=None, auth_key=None, username=None, password=None):
        """
        Initialize the client with provided configurations.

        url (str)         :     URL for the event consumer.
        auth_scheme (str) :     Scheme used for authentication.
        auth_key (str)    :     API key used in the authorization header.
        headers (str)     :     Any additional headers to be sent with event payload.
        """

        self.URL = url
        self.AUTH_SCHEME = auth_scheme
        self.AUTH_KEY = auth_key
        self.VERSION = version

        if auth_scheme == RouterConfiguration.AUTH_BASIC:
            self.lrs_client = RemoteLRS(
                version=self.VERSION,
                endpoint=self.URL,
                username=username,
                password=password
            )
        else:
            self.lrs_client = RemoteLRS(
                version=self.VERSION,
                endpoint=self.URL,
                auth=self.get_auth_header_value()
            )

    def get_auth_header_value(self):
        """
        Generate auth header value depending upon the client configurations.

        Returns:
            str
        """
        if self.AUTH_SCHEME and self.AUTH_SCHEME == RouterConfiguration.AUTH_BEARER and self.AUTH_KEY:
            return f'{self.AUTH_SCHEME} {self.AUTH_KEY}'

        return None

    def send(self, statement_data, event_name):
        """
        Send the xAPI statement to configured remote.

        Arguments:
            event_name (str)           :   name of the original event.
            statement_data (Statement) :   transformed xAPI statement

        Returns:
            requests.Response object
        """
        logger.debug('Sending xAPI statement of edx event "{}" to {}'.format(event_name, self.URL))

        response = self.lrs_client.save_statement(statement_data)
        if not response.success:
            logger.warning('{} request failed for sending xAPI statement of edx event "{}" to {}. '
                           'Response code: {}. Response: {}'.format(response.request.method, event_name, self.URL,
                                                                    response.response.code, response.data))
            raise EventNotDispatched
