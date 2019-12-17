import base64
import json
import os
from urllib.parse import quote
import sys
import logging

# from flask_session import Session
import requests
from flask import Flask, request, redirect, render_template

from song import Song

q = Song()

app = Flask(__name__)

app.secret_key = 'super secret s'
app.config['SESSION_TYPE'] = 'filesystem'

#  Client Keys
CLIENT_ID = "b5b1d37af53a40bbae71580c1c426782"
CLIENT_SECRET = "aadb1b4acb334c059711a6759619096e"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "http://localhost"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public user-read-currently-playing user-read-playback-state playlist-modify-private streaming user-modify-playback-state"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route('/access')
def get_access():
    access = json.load(open('response.json', 'r'))
    authorization_header = {"Authorization": "Bearer {}".format(access['access_token'])}

    auth_str = bytes('{}:{}'.format(CLIENT_ID, CLIENT_SECRET), 'utf-8')
    b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

    response = requests.post('https://accounts.spotify.com/api/token',
                             headers={'Authorization': f'Basic {b64_auth_str}'},
                             data={"grant_type": "refresh_token",
                                   'refresh_token': access['refresh_token']})

    data = dict(json.loads(response.text))
    print(data)
    for key, val in data.items():
        access[key] = val

    print(access)
    json.dump(access, open('response.json', 'w'))
    global q
    q.update(authorization_header)
    return access

@app.route('/main')
def go_to_main():
    if 'response.json' not in os.listdir('.'):
        return redirect('/login')

    return render_template('index.html')

@app.route('/')
def index():
    print('Reached')
    if 'response.json' not in os.listdir('.'):
        return redirect('/login')

    get_access()
    return render_template("index.html")

@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route('/display')
def display():
    global q
    return q.display()

@app.route('/queue')
def addsong():
    if 'response.json' not in os.listdir('.'):
        return redirect('/login')

    access = get_access()
    authorization_header = {"Authorization": "Bearer {}".format(access['access_token'])}
    song = request.args.get('song')

    global q
    return q.add(song, authorization_header)

@app.route("/callback")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    access = json.loads(post_request.text)

    json.dump(access, open('response.json', 'w'))

    return access

@app.route('/next')
def next():
    print('next called')
    global q
    q.next()
    return 'Next called'

@app.route('/search')
def search():
    if 'response.json' not in os.listdir('.'):
        return redirect('/login')

    access = get_access()
    authorization_header = {"Authorization": "Bearer {}".format(access['access_token'])}
    song = request.args.get('song')
    global q
    return q.search(song, authorization_header)

@app.route('/upnext')
def get_queue():
    global q
    return q.get_queue()

@app.route('/<r>')
def stat(r):
    print(r)
    return render_template(r)

if __name__ == "__main__":
    app.run(debug=True, port=PORT)