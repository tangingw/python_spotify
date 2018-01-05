## SPOTIFY API Grabber written in Flask (Python 3.6)

### Note
This is an experimental version of SPOTIFY API grabber. The author will constantly update the features. Use it as your own cause.

### Description
This is a simple [Spotify](https://www.spotify.com) API grabber that retrieves data from its own API [endpoint](https://beta.developer.spotify.com). As this software is still in its very early stage, the author advices not to use it for production, however the author will constantly update this repository as the project is meant to be in production.

### Synopsis
The purpose of building this API grabber is the first building block that the author wants to build for his own voice recognized Spotify player. Eventhough there are few items such as Alexa, Cortana, Google Home existed in the market, but not everyone can afford such devices, as well as not everyone can afford to have Spotify Premium account. The project uses Spotify Web API to control different devices through [Spotify Connect](https://www.spotify.com/my-en/connect/).

The author is currently swallowing javascript and jQuery so that can come out with a frontend UI that can control the usage of the API through Spotify Connect.

### Before you **git clone**
Before you download this repository, make sure that:
* Register yourself in the [Spotify Developer](https://beta.developer.spotify.com)
* Create your App in Spotify
* Whitelist your callback in this format *http://example.com/callback/* (a / at the back is a must)
* Grab both **client_id** and **client_secret**

### Once you **git clone**
Edit config.json
```json
{
    "callback_url": "http://example.com/callback/",
    "scope": "user-read-email user-read-birthdate user-read-playback-state",
    "state_msg": "<YOUR FAVOURITE MESSAGE>"
}
```

Edit credentials.json
```json
{
    "client_id": "<YOUR CLIENT_ID>",
    "client_secret": "<YOUR CLIENT_SECRET>"
}
```

For Spotify OAuth2 scopes, please refer to the [scope](https://developer.spotify.com/web-api/using-scopes/) page. 
Do not worry about token.json, it is a file that used by system to store token related data.

### After you **git clone**
On your terminal, run 
```bash
SHELL> cd ~/python_spotify
SHELL> python app.py
```

### After you **python app.y**
On your browser, type *http://example.com/spotify*

To retrieve your own data, type *http://example.com/spotify/me*


### Pull Request, Anyone?
contact me at [tangingw.pas@gmail.com](mailto:tangingw.pas@gmail.com)
