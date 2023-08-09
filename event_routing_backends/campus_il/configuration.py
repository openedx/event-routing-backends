import os
#from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from django.conf import settings

from configparser import ConfigParser
from enum import Enum
import logging

class Config():

    config: ConfigParser = ConfigParser()
    environment: Enum = None
    environmentStr: None

    def __init__(self, environment = None, environmentStr = None):
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'config.ini')

        self.config.read(path_config_file, encoding='utf-8')
        self.environment = environment
        self.environmentStr = environmentStr

    def Get(self, key):
        _envieronment = self.environment.value if self.environment else self.environmentStr
        if self.config.has_option(_envieronment, key):
            value = self.config.get(_envieronment, key)
        else:
            value = self.config.get('General', key)
            
        return value

class Environments(Enum):
    DEV = 'Dev'
    STAGE = 'Stage'
    PROD = 'Prod'

_environment_str = getattr(settings, 'CAMPUSIL_ENVIRONMET_NAME', '')

try:
    _environment = Environments[_environment_str.upper()]
    logging.info(f"MOE: Applied configuration of '{_environment_str}'.")
except KeyError:
    logging.error(f"MOE: The '{_environment_str}' is not configured in the configuration file. The default 'Stage' environment configuration is applied. Tip: check if CAMPUSIL_ENVIRONMET_NAME key exists in lms.yml")
    _environment = Environments.STAGE

config = Config(environment=_environment)