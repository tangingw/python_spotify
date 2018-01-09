import hashlib
import json
import requests
from flask import Flask
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for

from utils import Handler
from utils import auth
from utils import config


BASE_URL = "https://api.spotify.com"


app = Flask(__name__)
handler = Handler()


@app.route("/")
def hello_world():

    return "Hello World!"


@app.route("/authorize")
def authorize():

    client_id, _ = auth()
    config_content = config()

    authorize_url = "https://accounts.spotify.com/authorize/"

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": config_content["callback_url"],
        "state": hashlib.sha256(config_content["state_msg"].encode('utf-8')).hexdigest(),
        "scope": config_content["scope"]
    }

    response = requests.get(authorize_url, params=params)

    return redirect(response.url)


@app.route("/callback/")
def callback():

    callback_url = config()["callback_url"]
    callback_params = request.args

    if "error" in callback_params:

        return jsonify(
            error=callback_params.get("error"),
            state=callback_params.get("state")
        )

    post_data = {
        "grant_type": "authorization_code",
        "code": callback_params.get("code"),
        "redirect_uri": callback_url,
    }

    return handler.write_file_handler(post_data)


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

    return handler.write_file_handler(post_data)


@app.route("/spotify")
def get_spotify():

    player_info = handler.generic_handler(BASE_URL + "/v1/me/player", request.path)

    if player_info:

        return player_info

    return redirect(url_for("get_my_devices"))


@app.route("/spotify/me/devices")
def get_my_devices():

    return handler.generic_handler(BASE_URL + "/v1/me/player/devices", request.path)


@app.route("/spotify/me")
def get_spotify_me():

    return handler.generic_handler(BASE_URL + "/v1/me", request.path)


@app.route("/spotify/me/following")
def get_my_follow():

    params = {"type": "artist"}
    return handler.generic_handler(BASE_URL + "/v1/me/following", request.path, params=params)


@app.route("/spotify/me/playlists")
def get_my_playlist():

    return handler.generic_handler(BASE_URL + "/v1/me/playlists", request.path)


@app.route("/spotify/search")
def search_spotify():

    callback_params = request.args

    return handler.generic_handler(BASE_URL + "/v1/search", request.path, params=callback_params)


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8080)
