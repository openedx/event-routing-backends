import logging
import boto3
import json
from event_routing_backends.campus_il.configuration import config

class SQSService():
    
    sqs_service = None
    queue_url = None
    
    def __init__(self):
        
        self.queue_url = f'https://sqs.{config.Get("SQS_REGION_NAME")}.amazonaws.com/{config.Get("SQS_ACCOUNT_ID")}/{config.Get("SQS_NAME")}'
        self.sqs_service = boto3.client(
            'sqs',
            aws_access_key_id=config.Get("SQS_ACCESS_KEY"),
            aws_secret_access_key=config.Get("SQS_SECRET_KEY"),
            region_name=config.Get("SQS_REGION_NAME")
        )

    # Clear the queue
    def clear_queue(self):
        try:
            return self.sqs_service.purge_queue(QueueUrl=self.queue_url)
        except Exception as e:
            logging.error(f"Failed to clear SQS queue.\nException: {e}")

     # Send JSON to the queue
    def sent_data(self, data):
        json_payload = json.dumps(data)
    
        try:
            # Send the JSON payload with the unique MessageId to the SQS queue
            response = self.sqs_service.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json_payload,
                #DelaySeconds=5,
                #MessageGroupId='MOE_statments_group',  # Optional: Set a MessageGroupId for message ordering
            )
            
            logging.info(f"Data sent to SQS. Response: {response}.")
            return response
        except Exception as e:
            logging.error(f"Failed to send SQS data {data}.\nException: {e}")
    
    # Get JSON from the queue
    def get_data(self, amount=1, visibility_timeout=0):
        try:
            # Receive a message from the queue
            return self.sqs_service.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=amount,
                VisibilityTimeout=visibility_timeout,
                WaitTimeSeconds=0
            )
        except Exception as e:
            logging.error(f"Failed to get SQS data.\nException: {e}")
    
    # Delete the message from the queue 
    def delete_data(self, receipt_handle):
        try:
            response = self.sqs_service.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logging.info(f"Deleted SQS data, Response: {response}.")
            return response
        except Exception as e:
            logging.error(f"Failed to delete SQS data.\nException: {e}")
    
    # Get amount of items in queue
    def get_total_count(self):
        try:
            # Receive a message from the queue
            response = self.sqs_service.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['ApproximateNumberOfMessages']
            )
            return int(response['Attributes']['ApproximateNumberOfMessages'])
        except Exception as e:
            logging.error(f"Failed to get total count SQS data.\nException: {e}")