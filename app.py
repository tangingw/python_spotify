import hashlib
import base64
import json
import os
import pickle
import time
import requests
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for


app = Flask(__name__)


CRED_CONTENT = json.loads(open("credentials.json", "r").read())
CLIENT_ID = CRED_CONTENT["client_id"]
CLIENT_SECRET = CRED_CONTENT["client_secret"]


BASE_URL = "https://api.spotify.com"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize/"
TOKEN_URL = "https://accounts.spotify.com/api/token"


CONFIG = json.loads(open("config.json", "r").read())
CALLBACK_URL = CONFIG["callback_url"]
SCOPE = CONFIG["scope"]
STATE_MSG = CONFIG["state_msg"]


def store_previous_path(url_path):

    with open("url_path.p", "wb") as pickle_file:

        pickle.dump(url_path, pickle_file)


def get_previous_path():

    with open("url_path.p", "rb") as pickle_file:

        previous_path = pickle.load(pickle_file)

    return previous_path


def write_file_handler(post_data):

    secret_string = base64.b64encode(bytes((CLIENT_ID + ":" + CLIENT_SECRET).encode("utf-8")))

    headers = {
        "Authorization": "Basic %s" % secret_string.decode("utf-8")
    }

    response = requests.post(TOKEN_URL, headers=headers, data=post_data)

    current_time = int(time.time())
    expiry_time = current_time + 3600

    new_response = json.loads(response.text)
    new_response.update(
        {
            "start_time": current_time,
            "expiry_time": expiry_time
        }
    )

    with open("token.json", "w") as file:

        file.write(json.dumps(new_response))

    previous_path = get_previous_path()
    return redirect(previous_path)


def generic_handler(url, current_url, params=None):

    store_previous_path(current_url)

    if not os.path.exists("token.json"):

        return redirect(url_for("authorize"))

    with open("token.json", "r") as file:

        file_data = file.read()

    if not file_data:

        return redirect(url_for("authorize"))

    data = json.loads(file_data)

    if int(time.time()) > data["expiry_time"]:

        return redirect(url_for("refresh_token"))

    headers = {
        "Authorization": "Bearer " + data["access_token"]
    }

    response = requests.get(url, headers=headers, params=params)
    myown_data = json.loads(response.text)

    return jsonify(myown_data)


@app.route("/")
def hello_world():

    return "Hello World!"


@app.route("/authorize")
def authorize():

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": CALLBACK_URL,
        "state": hashlib.sha256(STATE_MSG.encode('utf-8')).hexdigest(),
        "scope": SCOPE
    }

    response = requests.get(AUTHORIZE_URL, params=params)

    return redirect(response.url)


@app.route("/callback/")
def callback():

    callback_params = request.args

    if "error" in callback_params:

        return jsonify(
            error=callback_params.get("error"),
            state=callback_params.get("state")
        )

    post_data = {
        "grant_type": "authorization_code",
        "code": callback_params.get("code"),
        "redirect_uri": CALLBACK_URL,
    }

    return write_file_handler(post_data)


@app.route("/refresh_token")
def refresh_token():

    with open("token.json", "r") as file:

        data = json.loads(file.read())

    if "refresh_token" not in data:

        return redirect(url_for("authorize"))

    post_data = {
        "grant_type": "refresh_token",
        "refresh_token": data["refresh_token"]
    }

    return write_file_handler(post_data)


@app.route("/spotify")
def get_spotify():

    player_info = generic_handler(BASE_URL + "/v1/me/player", request.path)

    if player_info:

        return player_info

    return redirect(url_for("get_my_devices"))


@app.route("/spotify/me/devices")
def get_my_devices():

    return generic_handler(BASE_URL + "/v1/me/player/devices", request.path)


@app.route("/spotify/me")
def get_spotify_me():


    return generic_handler(BASE_URL + "/v1/me", request.path)


@app.route("/spotify/me/following")
def get_my_follow():

    params = {"type": "artist"}
    return generic_handler(BASE_URL + "/v1/me/following", request.path, params=params)


@app.route("/spotify/me/playlists")
def get_my_playlist():

    return generic_handler(BASE_URL + "/v1/me/playlists", request.path)


@app.route("/spotify/search")
def search_spotify():

    callback_params = request.args

    return generic_handler(BASE_URL + "/v1/search", request.path, params=callback_params)


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8080)
