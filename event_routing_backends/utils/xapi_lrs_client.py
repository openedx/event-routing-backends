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

    def __init__(self, url=None, version=None, auth_scheme=None, auth_key=None, auth_pass=None, auth=None):
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
        self.AUTH_PASS = auth_pass
        self.VERSION = version
        self.AUTH = auth
        if self.AUTH_SCHEME == 'Basic' and self.AUTH_KEY is not None and self.AUTH_PASS is not None:
            self.lrs_client = RemoteLRS(
                version=self.VERSION,
                endpoint=self.URL,
                username=self.AUTH_KEY,
                password=self.AUTH_PASS
            )
        else:
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
        if self.AUTH:
            return f'{self.AUTH_SCHEME} {self.AUTH}'

        return None

    def send(self, json, event_name):
        """
        Send the xAPI statement to configured remote.

        Arguments:
            json (dict) :   transformed xAPI event json
            event_name (str) :   original name of the event that has now been transformed

        Returns:
            requests.Response object
        """
        ### WARNING!!!!!!!! The following 3 lines needs to be removed
        json['context']['extensions']['http://id.tincanapi.com/extension/tags'] = ['1.0', ]
        del(json['context']['extensions']['eventVersion'])
        del(json['version'])

        logger.info('Sending xAPI statement of {} to {}'.format(event_name, self.URL))
        response = self.lrs_client.save_statement(json)
        if not response:
            logger.error('Failed to send xAPI statement of {} to LRS at {}'.format(event_name, self.URL))
        else:
            if not response.success:
                logger.warning(
                    'LRS at {} has rejected the statement for event {}. Data: {}, Code: {}'.format(self.URL, event_name, response.data, response.response.code))
            else:
                logger.info(
                    'LRS at {} has accepted the statement for event {}. Data: {}, Code: {}'.format(self.URL, event_name, response.data, response.response.code))
