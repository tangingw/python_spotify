import base64
import json
import os
import pickle
import time
import requests
from flask import redirect
from flask import jsonify


def read_json(json_file):

    with open(json_file, "r") as file:

        content = json.loads(file.read())

    return content


def auth():

    credentials = read_json("credentials.json")

    return credentials["client_id"], credentials["client_secret"]


def config():

    return read_json("config.json")


class PickleStore(object):

    @staticmethod
    def store_previous_path(url_path):

        with open("url_path.p", "wb") as pickle_file:

            pickle.dump(url_path, pickle_file)

    @staticmethod
    def get_previous_path():

        with open("url_path.p", "rb") as pickle_file:

            previous_path = pickle.load(pickle_file)

        return previous_path


class Handler(object):

    def __init__(self):

        self.__client_id__, self.__client_secret__ = auth()

    def write_file_handler(self, post_data):

        token_url = "https://accounts.spotify.com/api/token"
        encoded_obj = bytes((self.__client_id__ + ":" + self.__client_secret__).encode("utf-8"))
        secret_string = base64.b64encode(encoded_obj)

        headers = {
            "Authorization": "Basic %s" % secret_string.decode("utf-8")
        }

        response = requests.post(token_url, headers=headers, data=post_data)

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

        previous_path = PickleStore.get_previous_path()
        return redirect(previous_path)

    def generic_handler(self, url, current_url, params=None):

        PickleStore.store_previous_path(current_url)

        if not os.path.exists("token.json"):

            return redirect("/authorize")

        with open("token.json", "r") as file:

            file_data = file.read()

        if (not file_data) or (int(time.time()) > json.loads(file_data)["expiry_time"]):

            return redirect("/authorize")

        data = json.loads(file_data)

        headers = {
            "Authorization": "Bearer " + data["access_token"]
        }

        response = requests.get(url, headers=headers, params=params)
        myown_data = json.loads(response.text)

        return jsonify(myown_data)
