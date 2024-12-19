import os
import requests
from dotenv import load_dotenv
from functools import wraps
from api_handler import APIHandler, wait_on_429

load_dotenv()


def reauthorize_on_401(func):
    @wraps(func)
    def wrapper_reauthorize(self, *args, **kwargs):
        if not self._access_token:
            self._authenticate()

        result = func(self, *args, **kwargs)

        if isinstance(result, tuple) and len(result) >= 2 and result[1] == 401:
            self._authenticate()

            result = func(self, *args, **kwargs)

        return result

    return wrapper_reauthorize


class SpotifyAPIHandler(APIHandler):
    def __init__(self):
        super().__init__(
            client_id=os.environ.get('SPOTIFY_ID')
            , client_secret=os.environ.get('SPOTIFY_SECRET')
        )

        self._access_token = ''
        self._token_type = ''

    def _authenticate(self) -> None:
        response, status = self.post(
            url='https://accounts.spotify.com/api/token'
            , headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            , payload={
                'grant_type': 'client_credentials'
            }
            , use_secret=True
        )

        if status == 200:
            self._access_token = response['access_token'].replace(' ', '')
            self._token_type = response['token_type'].replace(' ', '')

    @wait_on_429
    @reauthorize_on_401
    def get_track(self, track_id: str) -> dict:
        # if not self._access_token:
        #     self._authenticate()

        response, status = self.get(
            url=f'https://api.spotify.com/v1/tracks/{track_id}'
            , headers={'Authorization': f'{self._token_type}  {self._access_token}'}
        )

        if status == 200:
            return response
        # elif status == 401:
        #     self._authenticate()
        #     self.get_track(track_id=track_id)

        return response

    @wait_on_429
    @reauthorize_on_401
    def get_tracks(self, track_ids: list[str]) -> dict:
        ids = ','.join(track_ids)

        response, status = self.get(
            url=f'https://api.spotify.com/v1/tracks?ids={ids}'
            , headers={'Authorization': f'{self._token_type}  {self._access_token}'}
        )

        if status == 200:
            return response


if __name__ == '__main__':
    api = SpotifyAPIHandler()

    # print(api.get_track(track_id='5SuOikwiRyPMVoIQDJUgSV'))
    # print(api.get_tracks(track_ids=['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ', '2takcwOaAZWiXQijPHIx7B']))
