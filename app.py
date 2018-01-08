import hashlib
import base64
import json
import os
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


def write_file(post_data):

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

    return redirect(url_for("get_spotify"))


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

    return write_file(post_data)


@app.route("/spotify")
def get_spotify():

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

    response = requests.get(BASE_URL + "/v1/me/player", headers=headers)

    if not response.text:

        response = requests.get(BASE_URL + "/v1/me/player/devices", headers=headers)

    my_device = json.loads(response.text)

    #return json.dumps(myown_data, indent=4, ensure_ascii=False)
    return jsonify(my_device)


@app.route("/spotify/me")
def get_spotify_me():

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

    response = requests.get(BASE_URL + "/v1/me", headers=headers)
    myown_data = json.loads(response.text)

    return jsonify(myown_data)


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

    return write_file(post_data)


if __name__ == "__main__":

    app.run(host='0.0.0.0', port=8080)
