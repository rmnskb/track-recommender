import os
import requests
from dotenv import load_dotenv
from api_handler import APIHandler

load_dotenv()


class SpotifyAPIHandler(APIHandler):
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('SPOTIFY_ID')
            , client_secret=os.environ.get('SPOTIFY_SECRET')
        )

        self._access_token = ''
        self._token_type = ''

    def _authenticate(self):
        try:
            response = self.post(
                url='https://accounts.spotify.com/api/token'
                , headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                , payload={
                    'grant_type': 'client_credentials'
                }
                , use_secret=True
            )

            self._access_token = response['access_token']
            self._token_type = response['token_type']

            print(response)

        except requests.exceptions.HTTPError as err:
            print(err)

    def get_artists(self, artist_id: str) -> dict:
        ...


if __name__ == '__main__':
    api = SpotifyAPIHandler()

    print(api._authenticate())
