import requests
import time
import json
import os
import logging

def alert(event,thisHost,timestamp):
  logger = logging.getLogger('main')

  if 'name' in event['Actor']['Attributes']:
    nameValue = event['Actor']['Attributes']['name']
  else:
    # No name available, use ID instead
    nameValue = event['Actor']['ID']  

  ## Define payload
  payload = {
    "token": os.environ['token'],
    "host": thisHost,
    "time": timestamp,
    "name": nameValue,
    "type": event['Type'],
    "action": event['Action']
  }
  
  ## Perform request
  try:
    requests.post(
      "https://docker-notifications.nevishs.com", 
      data = json.dumps(payload),
      headers = {'Content-Type': 'application/json'}
    )

  except requests.exceptions.RequestException as e:
    logger.error('{}: {}'.format(__name__,e))
    
