# -*- coding: utf-8 -*-

""" Echobot using slackclient """

import os
import time

import slackclient

SLACK_BOT_NAME = os.environ.get('SLACK_BOT_NAME')

if SLACK_BOT_NAME is None:
    print('SLACK_BOT_NAME not set')
    exit(1)

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

if SLACK_BOT_TOKEN is None:
    print('SLACK_BOT_TOKEN not set')
    exit(1)

SLACK_CLIENT = slackclient.SlackClient(SLACK_BOT_TOKEN)
API_CALL = SLACK_CLIENT.api_call('users.list')
if API_CALL.get('ok'):
    # retrieve all users so we can find our bot
    USERS = API_CALL.get('members')
    for member in USERS:
        if 'name' in member and member.get('name') == SLACK_BOT_NAME:
            BOT_ID = member.get('id')
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


def get_mention(user):
    """
    Returns users mention
    """
    return '<@{user}>'.format(user=user)

BOT_MENTION = get_mention(BOT_ID)


def add_mention(user_mention, response):
    """
    Returns response mentioning the person who mentioned you
    """
    response_template = '{mention} ' + response
    return response_template.format(mention=user_mention)


def is_private(event):
    """Checks if private slack channel"""
    return event.get('channel').startswith('D')


def is_for_me(event):
    """Know if the message is dedicated to me"""
    # check if not my own event
    event_type = event.get('type')
    if (event_type and
            event_type == 'message' and not event.get('user') == BOT_ID):
        text = event.get('text')
        # in case it is a private message return true
        if text and is_private(event):
            return True
        # in case it is not a private message check mention
        if text and BOT_MENTION in text.strip().split():
            return True
    return None


def handle_request(message_text, channel, user):
    """
        Receives requests directed at the bot and determines if they
        are valid requests. If so, then acts on the requests. If not,
        returns back what it needs for clarification.
    """
    # removes first mention to the bot in public channels
    if not channel.startswith('D'):
        unmentioned_message = message_text.replace(BOT_MENTION, '', 1)
    else:
        unmentioned_message = message_text
    unmentioned_message = unmentioned_message.strip()

    # public channels
    if not channel.startswith('D'):
        user_mention = get_mention(user)
        unmentioned_message = add_mention(user_mention, unmentioned_message)

    # send messages to channel
    SLACK_CLIENT.api_call('chat.postMessage',
                          channel=channel,
                          text=unmentioned_message,
                          as_user=True)


def parse_slack_output(event_list):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    if event_list:
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
    if SLACK_CLIENT.rtm_connect():
        print('%s connected', __file__)
        while True:
            REQUEST, CHANNEL, TS, EVENT_USER = parse_slack_output(
                SLACK_CLIENT.rtm_read())
            if REQUEST and CHANNEL:
                print('slack_message:|%s|%s|%s|%s|',
                      str(REQUEST), str(CHANNEL),
                      str(TS), str(EVENT_USER))
                handle_request(REQUEST, CHANNEL, EVENT_USER)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print('Connection failed. Invalid Slack token or bot ID?')
