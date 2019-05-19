# -*- coding: utf-8 -*-
from os import environ  # get environment variables
import time
from slackclient import SlackClient

SLACK_BOT_NAME = environ.get('SLACK_BOT_NAME')

if SLACK_BOT_NAME is None:
    print('SLACK_BOT_NAME not set')
    exit(1)

SLACK_BOT_TOKEN = environ.get('SLACK_BOT_TOKEN')

if SLACK_BOT_TOKEN is None:
    print('SLACK_BOT_TOKEN not set')
    exit(1)

slack_client = SlackClient(SLACK_BOT_TOKEN)
api_call = slack_client.api_call('users.list')
if api_call.get('ok'):
    # retrieve all users so we can find our bot
    users = api_call.get('members')
    for user in users:
        if 'name' in user and user.get('name') == SLACK_BOT_NAME:
            BOT_ID = user.get('id')
else:
    print('Could not reach Slack with your SLACK_BOT_TOKEN. Please check if ' +
          'your SLACK_BOT_TOKEN and SLACK_BOT_NAME are both correct.')
    exit(1)

try:
    BOT_ID
except NameError:
    print('Could not find bot with the name ' + SLACK_BOT_NAME + '. Please ' +
          'check if your SLACK_BOT_TOKEN and SLACK_BOT_NAME are both correct.')
    exit(1)


# how the bot is mentioned on slack
def get_mention(user):
    return '<@{user}>'.format(user=user)

BOT_MENTION = get_mention(BOT_ID)


# give response mentioning the person who mentioned you
def add_mention(user_mention, response):
    response_template = '{mention} ' + response
    return response_template.format(mention=user_mention)


def is_private(event):
    """Checks if private slack channel"""
    return event.get('channel').startswith('D')


def is_for_me(event):
    """Know if the message is dedicated to me"""
    # check if not my own event
    type = event.get('type')
    if type and type == 'message' and not(event.get('user') == BOT_ID):
        text = event.get('text')
        # in case it is a private message return true
        if text and is_private(event):
            return True
        # in case it is not a private message check mention
        if text and BOT_MENTION in text.strip().split():
            return True


def handle_request(message, channel, ts, user):
    """
        Receives requests directed at the bot and determines if they
        are valid requests. If so, then acts on the requests. If not,
        returns back what it needs for clarification.
    """
    # removes first mention to the bot in public channels
    if not channel.startswith('D'):
        unmentioned_message = message.replace(BOT_MENTION, '', 1)
    else:
        unmentioned_message = message
    unmentioned_message = unmentioned_message.strip()

    # public channels
    if not channel.startswith('D'):
        user_mention = get_mention(user)
        unmentioned_message = add_mention(user_mention, unmentioned_message)

    # send messages to channel
    slack_client.api_call('chat.postMessage',
                          channel=channel,
                          text=unmentioned_message,
                          as_user=True)


def parse_slack_output(event_list):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    if len(event_list) > 0:
        for event in event_list:
            if is_for_me(event):
                return event['text'], \
                       event['channel'], \
                       event['ts'], \
                       event['user']
    return None, None, None, None

if __name__ == '__main__':
    print('%s running', __file__)
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print('%s connected', __file__)
        while True:
            request, channel, ts, user = parse_slack_output(
                slack_client.rtm_read())
            if request and channel:
                print('slack_message:|' + str(request) + '|' + str(channel) +
                      '|' + str(ts) + '|' + str(user) + '|')
                handle_request(request, channel, ts, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')
