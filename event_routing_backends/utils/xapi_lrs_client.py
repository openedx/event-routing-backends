"""
An LRS client for xAPI stores.
"""
from logging import getLogger

from tincan.remote_lrs import RemoteLRS

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

        if auth_key is None \
                and username is not None \
                and password is not None:
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
        if self.AUTH_SCHEME and self.AUTH_KEY:
            return f'{self.AUTH_SCHEME} {self.AUTH_KEY}'

        return None

    def send(self, statement_data):
        """
        Send the xAPI statement to configured remote.

        Arguments:
            statement_data (Statement) :   transformed xAPI statement

        Returns:
            requests.Response object
        """
        logger.info('Sending event json to %s', self.URL)
        response = self.lrs_client.save_statement(statement_data)

        if not response.success:
            logger.warning(
                'LRS at {} has rejected the statement for event {}. Data: {}, Code: {}'.format(
                    self.URL,
                    statement_data,
                    response.data,
                    response.response.code
                )
            )
            raise EventNotDispatched

        logger.info(
            'LRS at {} has accepted the statement for event {}. Data: {}, Code: {}'.format(
                self.URL,
                statement_data,
                response.data,
                response.response.code
            )
        )
