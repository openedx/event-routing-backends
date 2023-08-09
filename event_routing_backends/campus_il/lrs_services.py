import logging
import requests
from datetime import datetime, timedelta
from event_routing_backends.campus_il.configuration import config

# NOT IN USE TODAY !!!!!!!!!!!!
class LRSServices():
    external_services = []
    
    def __init__(self, cache):
        self.cache = cache
    
    @staticmethod
    def send_event(event, event_name, external_service):
        if external_service.name not in LRSServices.external_services.keys():
            pass
            # APIMOEService()
            # MyClass.static_variable += 1
            # print(f"Static variable value: {MyClass.static_variable}")
