import sys
import yaml
import logging

def load():
  ## Load config from file
  try:
    logger = logging.getLogger('main')
    with open('conf.yml', 'r') as file:
      config = yaml.safe_load(file)
  except:
    logger.error('Unable to load configuration - shutting down')
    sys.exit(1)

  ## Validate config
  if config:
    ## Settings
    if 'settings' in config:
      if 'logging' not in config['settings']:
        config['settings'] = {'logging':'info'}
      if 'exclusions' in config['settings'] and 'inclusions' in config['settings'] :
        logger.error('Both exclusions and inclusions specified in config. This is not supported - shutting down')
        sys.exit(1)
      if 'silence' in config['settings']:
        if 'start' in config['settings']['silence']:
            if not type(config['settings']['silence']['start']) == str:
              logger.error('Start time not in string format - shutting down')      
              sys.exit(1)
        if not 'start' in config['settings']['silence'] or not 'duration' in config['settings']['silence']:
          logger.error('No start and or duration time specified in silence window - shutting down')
          sys.exit(1)
        if 'exclusions' in config['settings']['silence'] and 'inclusions' in config['settings']['silence']:
          logger.error('Both exclusions and inclusions specified in config. This is not supported - shutting down')
          sys.exit(1)
    else:
      logger.warn('Settings not defined - loading defaults')
      config['settings'] = {'logging':'info'}

    ## Events
    if 'events' in config:
      pass
    else:
      logger.warn('No events have been specified so no alerts will be triggered')
      config['events'] = {}
    ## Integrations
    if 'integrations' in config:
      pass
    else:
      logger.warn('No integrations have been specified so no alerts will be triggered')
      config['integrations'] = {}
    ## Return
    return config
  else:
    logger.error('Unable to load configuration - shutting down')
    sys.exit(1)


  