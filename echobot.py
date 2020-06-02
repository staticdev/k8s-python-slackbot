# -*- coding: utf-8 -*-
"""Echobot using slackclient."""
import os

import slack

SLACK_BOT_NAME = os.environ.get("SLACK_BOT_NAME")

if SLACK_BOT_NAME is None:
    print("SLACK_BOT_NAME not set.")
    exit(1)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

if SLACK_BOT_TOKEN is None:
    print("SLACK_BOT_TOKEN not set.")
    exit(1)

WEB_CLIENT = slack.WebClient(token=SLACK_BOT_TOKEN)
RES = WEB_CLIENT.auth_test()
BOT_ID = RES["bot_id"]

try:
    BOT_ID
except NameError:
    print(
        "Could not find bot with the name "
        + SLACK_BOT_NAME
        + ". Please "
        + "check if your SLACK_BOT_TOKEN and SLACK_BOT_NAME are both correct."
    )
    exit(1)


def get_mention(user):
    """Returns users mention."""
    return "<@{user}>".format(user=user)


BOT_MENTION = get_mention(BOT_ID)


def add_mention(user_mention, response):
    """Returns response mentioning the person who mentioned you."""
    response_template = "{mention} " + response
    return response_template.format(mention=user_mention)


def is_private(event):
    """Checks if private slack channel."""
    return event.get("channel").startswith("D")


def is_for_me(event):
    """Know if the message is dedicated to me."""
    # check if not my own event
    event_type = event.get("type")
    if event_type and event_type == "message" and not event.get("user") == BOT_ID:
        text = event.get("text")
        # in case it is a private message return true
        if text and is_private(event):
            return True
        # in case it is not a private message check mention
        if text and BOT_MENTION in text.strip().split():
            return True
    return None


def parse_slack_output(data):
    """Returns text, channel, ts and user."""
    return data["text"], data["channel"], data["ts"], data["user"]


@slack.RTMClient.run_on(event="message")
def handle_request(**payload):
    """
        Receives requests directed at the bot and determines if they
        are valid requests. If so, then acts on the requests. If not,
        returns back what it needs for clarification.
    """
    data = payload["data"]
    web_client = payload["web_client"]
    message, channel, ts, user = parse_slack_output(data)
    print(
        "slack_message:|%s|%s|%s|%s|" % (str(message), str(channel), str(ts), str(user))
    )
    # removes first mention to the bot in public channels
    if not channel.startswith("D"):
        unmentioned_message = message.replace(BOT_MENTION, "", 1)
    else:
        unmentioned_message = message
    unmentioned_message = unmentioned_message.strip()

    # public channels
    if not channel.startswith("D"):
        user_mention = get_mention(user)
        unmentioned_message = add_mention(user_mention, unmentioned_message)

    # send messages to channel
    web_client.chat_postMessage(
        channel=channel, text=unmentioned_message, thread_ts=ts, as_user=True
    )


if __name__ == "__main__":
    print("{} running".format(__file__))
    WEB_CLIENT.start()
