# -*- coding: utf-8 -*-
"""Echobot using slackclient."""
import logging
import os
import sys
import urllib

import slack

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)
GLOBAL_STATE = {}

SLACK_BOT_NAME = os.environ.get("SLACK_BOT_NAME")

if SLACK_BOT_NAME is None:
    sys.exit("SLACK_BOT_NAME not set.")

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

if SLACK_BOT_TOKEN is None:
    sys.exit("SLACK_BOT_TOKEN not set.")


def get_mention(user):
    """Returns users mention."""
    return "<@{user}>".format(user=user)


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
        if text and get_mention(BOT_ID) in text.strip().split():
            return True
    return None


def parse_slack_output(data):
    """Returns text, channel, ts and user."""
    return data["text"], data["channel"], data["ts"], data["user"]


@slack.RTMClient.run_on(event="open")
def open_client(**payload):
    web_client = payload["web_client"]
    auth_result = web_client.auth_test()
    GLOBAL_STATE.update({"bot_id": auth_result["bot_id"]})
    LOGGER.info(f"cached: {GLOBAL_STATE}")


@slack.RTMClient.run_on(event="message")
def handle_request(**payload):
    """
        Receives requests directed at the bot and determines if they
        are valid requests. If so, then acts on the requests. If not,
        returns back what it needs for clarification.
    """
    data = payload["data"]
    if data.get("bot_id", None) == GLOBAL_STATE["bot_id"]:
        LOGGER.debug("Skipped as it's me")
        return
    web_client = payload["web_client"]
    message, channel, ts, user = parse_slack_output(data)
    LOGGER.debug(
        "slack_message:|%s|%s|%s|%s|" % (str(message), str(channel), str(ts), str(user))
    )
    # removes first mention to the bot in public channels
    if not channel.startswith("D"):
        unmentioned_message = message.replace(get_mention(BOT_ID), "", 1)
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
    LOGGER.info("{} running".format(__file__))
    RTM_CLIENT = slack.RTMClient(token=SLACK_BOT_TOKEN)
    RTM_CLIENT.start()
