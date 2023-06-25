from event_routing_backends.campus_il.configuration import config
from event_routing_backends.campus_il.moe_api_service import APIMOEService
from event_routing_backends.campus_il.moe_mapping_service import MOEMapping

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

class MOE():

    cache = None
    api_service = None
    map_service = None
    
    def __init__(self, cache):
        self.cache = cache
        self.api_service = APIMOEService(self.cache)
        self.map_service = MOEMapping()
    
    def sent_event(self, event, event_name):
        event = self.map_service.map_event(event=event)
        logger.info(f"MOE event prepared: {event}")
        logger.info(f'MOE event verb type: {event["verb"]["id"]}')
        response_data = self.api_service.send_statment([event])
        logger.info(f"MOE event '{event_name}' sent. Response: {response_data}")
        


# Cache dictionary to store data and it expiration time
cache = {}

# MOE service that will adapt and send event to the MOE server
moe_service = MOE(cache)