from configparser import ConfigParser
from enum import Enum
import os

class Config():

    config: ConfigParser = ConfigParser()
    environment: Enum = None

    def __init__(self, environment):
        path_current_directory = os.path.dirname(__file__)
        path_config_file = os.path.join(path_current_directory, 'config.ini')

        self.config.read(path_config_file, encoding='utf-8')
        self.environment = environment

    def Get(self, key):
        if self.config.has_option(self.environment.value, key):
            value = self.config.get(self.environment.value, key)
        else:
            value = self.config.get('General', key)
            
        return value

class Environments(Enum):
    STAGE = 'Stage'
    PROD = 'Prod'
    
config = Config(Environments.STAGE)