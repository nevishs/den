import conf
import log
import sys
import os
import yaml
import datetime
import time
import signal
import docker

def shutdown(_signo, _stack_frame):
  logger.info('Recieved {}, shutting down'.format(_signo))
  sys.exit(0)

def sendAlert(event,timestamp):
  ''' Check which integrations are enabled and send alerts '''
  logger.info('Alert triggered: {},{},{}'.format(event['Type'],event['Action'],event['Actor']['ID']))
  if 'notify' in config['integrations']:
    if config['integrations']['notify']['enabled']:
      import notify
      notify.alert(event,thisHost,timestamp)


def silenceWindow(event):
  ''' Returns true if event is in silence window '''
  ## Check silence window is set
  if 'silence' in config['settings']:
    #### Convert start_time into epoch
    startTime = str(config['settings']['silence']['start'])
    ## get date/time as string interpolating the configured start_time
    startTimeStr = datetime.datetime.now().strftime("%Y-%m-%dT"+startTime+":%S.%fZ")
    ## convert string into datetime object so that it can be converted into epoch
    startTimeObject = datetime.datetime.strptime(startTimeStr, '%Y-%m-%dT%H:%M:%S.%fZ')
    ## convert into epoch
    startTimeEpoch = startTimeObject.timestamp()
    ## Add duration to epoch
    endTimeEpoch = startTimeEpoch + int(config['settings']['silence']['duration']) * 60
    ## Get current_time in epoch
    currentTimeEpoch = datetime.datetime.now().timestamp()

    ## Check inclusion / exclusion
    if 'name' in event['Actor']['Attributes']:
      eventActorName = event['Actor']['Attributes']['name']
    else:
      # No name available, use ID instead
      eventActorName = event['Actor']['ID']

    ## Is the event within the silence window
    if currentTimeEpoch > startTimeEpoch and currentTimeEpoch < endTimeEpoch:
      excludedFromSilence = False
      ## Is it excluded from the silence window
      
      if 'exclusions' in config['settings']['silence']:
        if includeExclude(eventActorName,config['settings']['silence']['exclusions']):
          excludedFromSilence = True
          logger.debug('EVENT EXCLUDED FROM SILENCE WINDOW')
      
      if 'inclusions' in config['settings']['silence']:
        if not includeExclude(eventActorName,config['settings']['silence']['inclusions']):
          excludedFromSilence = True
          logger.debug('EVENT EXCLUDED FROM SILENCE WINDOW')

      if not excludedFromSilence:
        return True
    else:
      ## Event not in silence window
      return False

def includeExclude(string,listOfStrings):
  ''' Does the string exist in the list of strings '''
  for i in listOfStrings:
    if i in string:
      return True
  return False


def main():
  ''' Look for any event on the event stream that matches the defined event types  '''
  for event in stream:
    logger.debug('Event: {}'.format(event))
    eventType = event['Type']
    eventAction = event['Action']
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['time']))
    if 'name' in event['Actor']['Attributes']:
      eventActorName = event['Actor']['Attributes']['name']
    else:
      # No name available, use ID instead
      eventActorName = event['Actor']['ID']
    
    ## Should the event trigger an alert
    if eventType in config['events']:
      if eventAction in config['events'][eventType]:
        if 'exclusions' in config['settings']:
          if not includeExclude(eventActorName,config['settings']['exclusions']):
            if not silenceWindow(event):
              sendAlert(event,timestamp)
        elif 'inclusions' in config['settings']:
          if includeExclude(eventActorName,config['settings']['inclusions']):
            if not silenceWindow(event):
              sendAlert(event,timestamp)
          
        else:
          ## If include or exclude lists do not exist, default to include
          if not silenceWindow(event):
            sendAlert(event,timestamp)       

if __name__ == '__main__':
  signal.signal(signal.SIGINT, shutdown)
  signal.signal(signal.SIGTERM, shutdown)
  logger = log.load()
  config = conf.load()
  try:
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    stream = client.events(decode=True)
    thisHost = client.info()['Name']
  except:
    logger.info('Failed to connect to Docker event stream')
    shutdown()

  logger.info('Starting up')
  logger.info('Token: {}'.format(os.environ['token']))
  main()