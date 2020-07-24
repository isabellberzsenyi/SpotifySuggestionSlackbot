import os
from genre_list import genre_list
import random
import json
from dotenv import load_dotenv
from setup_spotify import *


spotify_cid = os.getenv('SPOTIFY_CID')
spotify_secret = os.getenv('SPOTIFY_SECRET')
sp = create_spotify_client(spotify_cid, spotify_secret)


def showGenres():
    genre_recs_show = []
    genre_recs_value = []
    rec_number = []
    i = 0
    while i < 6:
        r = random.randint(1, 75)
        if r not in rec_number:
            rec_number.append(r)
            genre_recs_value.append(genre_list[r])
            i = i + 1
    for x in genre_recs_value:
        if "-" in x:
            x = x.replace("-", " ")
        genre_recs_show.append(x.capitalize())
    return genre_recs_show, genre_recs_value


def getRec(genre):
    response = sp.recommendations(seed_genres=[genre])
    if response['tracks'] == []:
        url = randomSong()
    else:
        url = response['tracks'][0]['external_urls']['spotify']
        print(url)
    return url
