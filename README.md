# Docker Event Notification (DEN)

### What is it?
A tiny container that checks local Docker event in real-time and sends them out to the application.

### Features
- Super light-weight container.
- Customisable event triggers.
- No exposed ports.

### Deployment
1. If you deployed it via the application, no further actions are required.
2. If you want to deploy it manually by having a customised image, you <b>MUST</b> follow the requirements below:
    - NAME      has to be docker-event-notification
    - TOKEN     has to match the token generated on the notification screen of the application
    - TAG       has to match the last uploaded tag version on [this image](https://hub.docker.com/r/nevishs/den/tags) e.g. 0.3

```
docker run -d --name {NAME} \
-v /var/run/docker.sock:/var/run/docker.sock \
-e token={TOKEN} \
{YOUR_IMAGE}:{TAG}

# example
docker run -d --name docker-event-notification \
-v /var/run/docker.sock:/var/run/docker.sock \
-e token=XXXXX \
nevishs/dem:0.3
```
### Configuration
Example `conf.yml` with a subset of available event types that will trigger a notification. For a full list of all available event types please see the official [Docker Events](https://docs.docker.com/engine/reference/commandline/events/).

```
settings:
  logging: info ## Log verbosity <debug, info (default), warn, error>
  exclusions: ## The name of any actors (containers, networks etc) you want to exclude from alerts
    - foo
  inclusions: ## If specified, only events from these actors will be alerted on. Any actors not in this list are implicitly excluded, therefore this is mutually exclusive with the above `exclusions` option.
    - foo
  silence: ## Time window where alerts will be silenced
    start: "02:00" ## Start of the silence window in 24 hour format
    duration: 120 ## Duration in minutes for the window to last
    exclusions: ## The name of any actors (containers, networks etc) you want to exclude from the silence window
      - foo
    inclusions: ## If specified, only events from these actors will be included in the silence window. Any actors not in this list are implicitly excluded, therefore this is mutually exclusive with the above `exclusions` option.
      - foo

events: ## The Docker event types that you want to trigger alerts for
  container: 
    - 'health_status: unhealthy'
    - oom
    - destroy
    - create
  image: 
    - delete
  plugin:
    - install
    - remove
  volume: 
    - destroy
    - create
  network:
    - destroy
  daemon:
    - reload
  service:
    - remove
  node:
    - remove
  secret:
    - remove
  config:
    - remove

integrations:
  notify:
    enabled: True
```
