from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

cid = 'd06605a0954e4edd9a373deba0c1676f'
secret = 'c8d55b932dd942fba41c6ab23a1d344f'

client_credentials_manager = SpotifyClientCredentials(
    client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


tokens = {}
with open('configs.json') as json_data:
    tokens = json.load(json_data)

slack_events_adapter = SlackEventAdapter(
    tokens.get("slack_signing_secret"), "/slack/events")
slack_client = SlackClient(tokens.get("slack_bot_token"))

# responds to an app mention


def randomSong():
    characters = 'abcdefghijklmnopqrstuvwxyz'
    randNum = random.randint(0, 25)
    randChar = characters[randNum]

    randSearch = '%' + randChar + '%'
    results = sp.search(q=randSearch, type='track', limit=1, offset=1)
    url = results['tracks']['items'][0]['external_urls']['spotify']
    return url


@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    message = event_data["event"]
    channel = message["channel"]
    song = randomSong()
    send_message = song
    # "https://open.spotify.com/track/3EuSjRC1jKGe6h3Nc9haWn?si=hCxSFkrYQ0KJ77rg7oQROQ"
    slack_client.api_call("chat.postMessage",
                          channel=channel, text=send_message)

# responds to a message that contains recommend


@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if message.get("subtype") is None and "recommend" in message.get('text'):
        song = randomSong()
        channel = message["channel"]
        send_message = "here's my recommendation: " + song
        slack_client.api_call("chat.postMessage",
                              channel=channel, text=send_message)


@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


slack_events_adapter.start(port=3000)
