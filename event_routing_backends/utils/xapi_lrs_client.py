"""
An LRS client for xAPI stores.
"""
from logging import getLogger

from tincan.remote_lrs import RemoteLRS

logger = getLogger(__name__)


class LrsClient:
    """
    An LRS client for xAPI stores.
    """

    def __init__(self, url=None, version=None, auth_scheme=None, auth_key=None):
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

        self.lrs_client = RemoteLRS(
            version=self.VERSION,
            endpoint=self.URL,
            auth=self.get_auth_header_value(),
        )

    def get_auth_header_value(self):
        """
        Generate auth header value depending upon the client configurations.

        Returns:
            str
        """
        if self.AUTH_SCHEME:
            return f'{self.AUTH_SCHEME} {self.AUTH_KEY}'

        return None

    def send(self, statement):
        """
        Send the xAPI statement to configured remote.

        Arguments:
            statement (Statement) :   transformed xAPI statement

        Returns:
            requests.Response object
        """
        logger.info('Sending event json to %s', self.URL)
        self.lrs_client.save_statement(statement)
