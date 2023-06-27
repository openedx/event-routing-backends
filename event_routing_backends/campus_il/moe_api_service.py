import logging
import requests
from datetime import datetime, timedelta
from event_routing_backends.campus_il.configuration import config

class APIMOEService():
    service_config = {}
    
    @property
    def token(self):
        # Check if token is in cache and not expired
        if 'token' in self.cache and self.cache['expiry'] > datetime.now():
            return self.cache['token']

        # Token not found in cache or expired, refresh it
        token_expiration_minutes = int(config.Get("API_HOST_TOKEN_EXPIRATION"))
        token = self.__refresh_token(self.service_config)
        expiry = datetime.now() + timedelta(minutes=token_expiration_minutes)  # Assuming token expires in 1 hour

        # Save the refreshed token and its expiry time in cache
        self.cache['token'] = token
        self.cache['expiry'] = expiry

        return token
    
    #%% Init section

    def __init__(self, cache):
        self.cache = cache
        
    def __refresh_token(self, service_config):
       
        # Client ID and secret
        client_id = config.Get("API_HOST_CLIENT_ID")
        client_secret = config.Get("API_HOST_CLIENT_SECRET")

        # Request parameters
        token_type = config.Get("API_HOST_TOKEN_TYPE")
        grant_type = config.Get("API_HOST_GRANT_TYPE")
        scope = config.Get("API_HOST_SCOPE")

        # Request headers
        headers = {
            "Content-Type": config.Get("API_HOST_TOKEN_CONTENT_TYPE")
        }

        # Endpoint URL
        endpoint = service_config.get("endpoints", {}).get("token", 
            f'https://{config.Get("API_HOST_NAME")}/{config.Get("API_HOST_TOKEN_URL")}?grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&scope={scope}&token_type={token_type}')
        #endpoint = f'https://{config.Get("API_HOST_NAME")}/{config.Get("API_HOST_TOKEN_URL")}?grant_type={grant_type}&client_id={client_id}&client_secret={client_secret}&scope={scope}&token_type={token_type}'

        access_token = None
        try:
            # Send the request
            response = requests.post(endpoint, headers=headers)
            
            # Get the response data
            data = response.json()

            # Access the token
            access_token = data.get("access_token")
            
            logging.info(f"Access token: {access_token}")
        except Exception as e:
            logging.info("Failed to obtain access token.")
            logging.info(f"Exception: {e}")
        
        return access_token

    def send_statment(self, events, service_config):
        self.service_config = service_config
        
        # Request headers
        headers = {
            "Authorization": f'{config.Get("API_HOST_TOKEN_TYPE")} {self.token}',
            "Content-Type": config.Get("API_HOST_STATEMENTS_CONTENT_TYPE")
        }

        # Endpoint URL
        endpoint = service_config.get("endpoints", {}).get("statements", 
            f'https://{config.Get("API_HOST_NAME")}/{config.Get("API_HOST_STATEMENTS_URL")}')

        post_data = events
        response_data = None
        
        try:
            # Send the request
            response = requests.post(endpoint, headers=headers, json=post_data)
            
            # Get the response data
            response_data = response.json()

            logging.info(f"MOE response data: {response_data}")
        except Exception as e:
            logging.info(f"Failed to send event to MOE. Exception: {e}")
        
        return response_data