#!/usr/bin/env python
import datetime
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

EVENT_LOG_DIR = 'data/events'
PROFILE_LOG_DIR = 'data/user_profiles'

import time
from slackclient import SlackClient


def process_messages(client):
    if client.rtm_connect():
        while True:
            for event in client.rtm_read():
                now = datetime.datetime.now()
                if log.isEnabledFor(logging.DEBUG):
                    filename = '{t}-{event[type]}.json'.format(
                        t=now.isoformat(), event=event
                    )
                    with open(os.path.join(EVENT_LOG_DIR, filename), 'w') as f:
                        json.dump(event, f, sort_keys=True, indent=4)
                log.debug(event)
                if event['type'] == 'team_join':
                    log.info('posted welcome to {user[name]}', user=event['user'])
                    client.api_call('chat.postMessage',
                        channel='@' + event['user'],
                        username='slackbot',
                        text=os.getenv('WELCOME_MESSAGE'),
                    )
            time.sleep(1)
    else:
        print("Connection Failed, invalid token?")


def teambuilder():
    if log.isEnabledFor(logging.DEBUG):
        os.makedirs(EVENT_LOG_DIR, exist_ok=True)
        os.makedirs(PROFILE_LOG_DIR, exist_ok=True)

    token = os.getenv("SLACK_TOKEN")
    if not token:
        raise RuntimeError('teambuilder requires env variable SLACK_TOKEN')

    client = SlackClient(token)
    process_messages(client)


if __name__ == '__main__':
    teambuilder()
