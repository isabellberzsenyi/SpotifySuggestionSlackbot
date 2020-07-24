import os
import json
from dotenv import load_dotenv
import random
from setup_server import *
from setup_spotify import *
from setup_slack_adapter import *
from flask import Flask, request, Response, jsonify

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

spotify_cid = os.getenv('SPOTIFY_CID')
spotify_secret = os.getenv('SPOTIFY_SECRET')
slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
slack_bot_secret = os.getenv('SLACK_BOT_SECRET')

app = create_flask_app()

sp = create_spotify_client(spotify_cid, spotify_secret)

slack_events_adapter, slack_client = create_slack_bot_adapter(
    slack_bot_token, slack_bot_secret, app)


def randomSong():
    characters = 'abcdefghijklmnopqrstuvwxyz'
    randNum = random.randint(0, 25)
    randChar = characters[randNum]

    randSearch = '%' + randChar + '%'
    results = sp.search(q=randSearch, type='track', limit=1, offset=1)
    url = results['tracks']['items'][0]['external_urls']['spotify']
    return url

# Simple helper function to parse the message
def getMrkdwnURL(song):
    return "<"+song+"|Hummm...How about this?>"

@app.route('/hum', methods=['POST'])
def hum():
    search = request.form['text']
    result = sp.search(q=search, type='track', limit=1, offset=1)
    url = result['tracks']['items'][0]['external_urls']['spotify']
    response = slack_client.api_call(
        "chat.postMessage",
        channel=request.form['channel_id'],
        text=url,
        username='pythonbot',
        icon_emoji=':robot_face:'
    )
    return(render_message(response['message']['text']))

def render_message(message):
    return jsonify({"response_type": "in_channel", "text": f"{message}"})

# responds to an app mention
@slack_events_adapter.on("app_mention")
def handle_mention(event_data):
    message = event_data["event"]
    channel = message["channel"]
    song = randomSong()
    song_url_mrkdwn = getMrkdwnURL(song)
    slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            unfurl_links=True,
            text=song_url_mrkdwn,
            mrkdwn=True,
    )

# responds to a message that contains recommend
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]
    if message.get("subtype") is None and "recommend" in message.get('text'):
        song = randomSong()
        channel = message["channel"]
        song_url_mrkdwn = getMrkdwnURL(song)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            unfurl_links=True,
            text=song_url_mrkdwn,
            mrkdwn=True,
        )


@ slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))
