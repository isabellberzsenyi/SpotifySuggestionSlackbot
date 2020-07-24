import os
import json
from dotenv import load_dotenv
from setup_server import *
from setup_spotify import *
from setup_slack_adapter import *
import logging
import random
from flask import Flask, request, Response, jsonify, make_response
from rec_genre import *


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


def randomSong(genre=''):
    characters = 'abcdefghijklmnopqrstuvwxyz'
    randNum = random.randint(0, 25)
    randChar = characters[randNum]
    randSearch = '%' + randChar + '%'

    if genre:
        genre_words = genre.split()
        randSearch += ' genre:' + ' '.join(genre_words)

    track_results = sp.search(q=randSearch, type='track', limit=50)
    if int(track_results['tracks']['total']) > 0:
        item = random.choice(track_results['tracks']['items'])
        track_url = item['external_urls']['spotify']
    else:
        track_results = sp.search(
            q='%' + randChar + '%', type='track', limit=50)
        item = random.choice(track_results['tracks']['items'])
        track_url = track_results['tracks']['items'][0]['external_urls']['spotify']
    return track_url

# Simple helper function to parse the message


def getMrkdwnURL(song):
    if song:
        return "<"+song+"|Hummm...How about this?>"
    else:
        None


@app.route('/hum', methods=['POST'])
def hum():
    search = request.form['text']
    if search:
        song = randomSong(search)
    else:
        song = randomSong()
    song = getMrkdwnURL(song)
    response = slack_client.api_call(
        "chat.postMessage",
        channel=request.form['channel_id'],
        text=song,
        username='pythonbot',
        icon_emoji=':robot_face:'
    )
    return make_response("", 200)
    # return(render_message(response['message']['text']))


# def render_message(message):
#     return jsonify({"response_type": "in_channel", "text": f"{message}"})


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
    return make_response("", 200)


@ slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))


@app.route('/genre', methods=['POST'])
def genre():
    text, value = showGenres()
    response = slack_client.api_call(
        "chat.postMessage",
        channel=request.form['channel_id'],
        text="Pick a genre",
        attachments=json.dumps(
            [
                {
                    "text": "Choose a genre",
                    "fallback": "If you could read this message, you'd be choosing something fun to do right now.",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "callback_id": "genre_selection",
                    "actions": [
                        {
                            "name": "genre_selection",
                            "text": "Pick a genre...",
                            "type": "select",
                            "options": [
                                {
                                    "text": f"{text[0]}",
                                    "value": f"{value[0]}"
                                },
                                {
                                    "text": f"{text[1]}",
                                    "value": f"{value[1]}"
                                },
                                {
                                    "text": f"{text[2]}",
                                    "value": f"{value[2]}"
                                },
                                {
                                    "text": f"{text[3]}",
                                    "value": f"{value[3]}"
                                },
                                {
                                    "text": f"{text[4]}",
                                    "value": f"{value[4]}"
                                }
                            ]
                        }
                    ]
                }
            ]
        )
    )
    return make_response("", 200)


@app.route('/genre_resp', methods=['POST'])
def genre_resp():
    form_json = json.loads(request.form["payload"])
    # call_id = form_json["callback_id"]
    selection = form_json["actions"][0]["selected_options"][0]["value"]
    text, value = showGenres()

    url = getRec(selection)
    song_url_mrkdwn = getMrkdwnURL(url)
    slack_client.api_call(
        "chat.postMessage",
        channel=form_json["channel"]["id"],
        unfurl_links=True,
        text=song_url_mrkdwn,
        mrkdwn=True,
        attachments=[]
    )
    return make_response("", 200)


# Start the server on port 3000
if __name__ == "__main__":
    app.run(port=int(os.getenv('PORT', 3000)))
