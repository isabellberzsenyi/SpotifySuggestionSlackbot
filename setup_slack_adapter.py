from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient

def create_slack_bot_adapter(token, secret, server):
    slack_events_adapter = SlackEventAdapter(secret, "/slack/events", server)

    slack_client = SlackClient(token)

    return slack_events_adapter, slack_client