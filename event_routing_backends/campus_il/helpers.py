import re

from celery.task import periodic_task, task
from celery.schedules import crontab

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
        logger.info(f"MOE: event prepared: {event}")
        logger.info(f'MOE: event verb type: {event["verb"]["id"]}')
        response_data = self.sqs_service.sent_data(event)
        logger.info(f"MOE: event '{event_name}' sent. Response: {response_data}")
        
    # sending all sqs events to moe lrs service
    def sent_sqs_events_moe(self, task_data):
        logger.info(f'MOE: Got data from the task: {task_data}')
        logger.info(f'MOE: Start events send from SQS to MOE LRS')
        event = None
        is_have_events = True
        
        while is_have_events:
            try:
                response = self.sqs_service.get_data(
                    amount=int(config.Get("SQS_MAX_ITEMS_ONE_TIME")), 
                    visibility_timeout=int(config.Get("SQS_VISIBILITY_TIMEOUT")))
                
                if isinstance(response, dict) and 'Messages' in response:
                    messages = response['Messages']
                    
                    for message in messages:
                        receipt_handle = message['ReceiptHandle']
                        event = message['Body']

                        # send to MOE
                        logger.info(f'MOE: Got event from SQS start send the event to MOE: {event}')
                        response_moe = self.api_service.send_statment(events_str=f'[{event}]')
                        logger.info(f'MOE: Sent event to MOE, response: {response_moe}')
                        is_guid_list = self.__is_list_of_guid_strings(response_moe)

                        if is_guid_list:
                            try:
                                # delete from queue of SQS
                                self.sqs_service.delete_data(receipt_handle)
                                logger.info(f'MOE: Event deleted from SQS: {event}')
                            except Exception as e:
                                logger.error(f'MOE: Event deletion from SQS is FAILED!/nEvent: {event}, Exception: {e}') 
                                #TODO: ADD EMAIL SEND TO THE ADMIN
                        else:
                            logger.error(f'MOE: Sending event to MOE is FAILED!/nMOE response: {response_moe}/nEvent: {event}')
                            #TODO: ADD EMAIL SEND TO THE ADMIN
                else:
                    is_have_events = False

                _total_items = self.sqs_service.get_total_count()
                logger.info(f'MOE: Total item in SQS: {_total_items}')
            except Exception as e:
                logger.error(f'MOE: Getting events from SQS is FAILED!/nException: {e}')
                        
    def __is_guid_string(self, string):
        # Regex pattern to match GUID format
        guid_pattern = r'^\{?[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}\}?$'

        # Check if the string matches the GUID pattern
        if re.match(guid_pattern, string, re.IGNORECASE):
            return True
        else:
            return False

    def __is_list_of_guid_strings(self, lst):
        # Check if each string in the list is a valid GUID string
        for item in lst:
            if not self.__is_guid_string(item):
                return False
        return True

cron_grade_settings = {
        'minute': '*/1',
        'hour': '*',
        'day_of_week': '*',
        'day_of_month': '*',
        'month_of_year': '*',
    }

@periodic_task(run_every=crontab(**cron_grade_settings))
def sent_sqs_events_to_moe_static(**data):
    moe_service.sent_sqs_events_moe(data)

# Cache dictionary to store data and it expiration time
cache = {}

# MOE service that will adapt and send event to the MOE server
moe_service = MOE(cache)

