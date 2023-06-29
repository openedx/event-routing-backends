from event_routing_backends.campus_il.configuration import config
from event_routing_backends.campus_il.moe_api_service import APIMOEService
from event_routing_backends.campus_il.moe_mapping_service import MOEMapping
from event_routing_backends.campus_il.sqs_service import SQSService

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
        self.sqs_service = SQSService()
    
    def sent_event(self, event, event_name, service_config):
        event = self.map_service.map_event(event=event)
        logger.info(f"MOE event prepared: {event}")
        logger.info(f'MOE event verb type: {event["verb"]["id"]}')
        #response_data = self.api_service.send_statment([event], service_config)
        response_data = self.sqs_service.sent_data(event)
        logger.info(f"MOE event '{event_name}' sent. Response: {response_data}")
        
        #self.sqs_service.clear_queue(event)
        


# Cache dictionary to store data and it expiration time
cache = {}

# MOE service that will adapt and send event to the MOE server
moe_service = MOE(cache)