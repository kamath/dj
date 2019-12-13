import json
from flask import Flask, request, redirect, g, render_template, session
from flask_session import Session
import requests
from song import Song
from urllib.parse import quote
import time
import base64

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response.


app = Flask(__name__)
sess = Session()

app.secret_key = 'super secret s'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
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

global q
q = Song()

def get_access():
    authorization_header = {"Authorization": "Bearer {}".format(session['response']['access_token'])}

    auth_str = bytes('{}:{}'.format(CLIENT_ID, CLIENT_SECRET), 'utf-8')
    b64_auth_str = base64.b64encode(auth_str).decode('utf-8')

    response = requests.post('https://accounts.spotify.com/api/token',
                             headers={'Authorization': f'Basic {b64_auth_str}'},
                             data={"grant_type": "refresh_token",
                                   'refresh_token': session['response']['refresh_token']})

    data = dict(json.loads(response.text))
    print(data)
    for key, val in data.items():
        session['response'][key] = val

    print(session['response'])
    global q
    q.update(authorization_header)
    return session['response']

@app.route('/')
def index():
    if 'response' not in session:
        return redirect('/login')

    get_access()

    authorization_header = {"Authorization": "Bearer {}".format(session['response']['access_token'])}
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("index.html", sorted_array=display_arr)

@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route('/queue')
def addsong():
    song = request.args.get('song')
    global q
    return q.add(song)

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
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    session['response'] = response_data

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True, port=PORT)
