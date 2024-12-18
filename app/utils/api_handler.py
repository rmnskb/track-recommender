import requests


class APIHandler:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        if client_id and client_secret:
            self._client_id = client_id
            self._client_secret = client_secret

    def post(self, url, headers, payload, use_secret: bool = False, **kwargs) -> dict:
        if use_secret and self._client_id and self._client_secret:
            payload['client_id'] = self._client_id
            payload['client_secret'] = self._client_secret

        if kwargs:
            payload.update(kwargs)

        try:
            response = requests.post(url=url, headers=headers, data=payload)
            response.raise_for_status()

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as err:
                print(err)
                return {
                    'response': response.text
                }
        except requests.exceptions.HTTPError as err:
            print(err)
            return {}

    @staticmethod
    def get(url, **kwargs) -> dict:
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()

            try:
                return response.json()
            except requests.exceptions.JSONDecodeError as err:
                print(err)
                return {
                    'response': response.text
                }
        except requests.exceptions.HTTPError as err:
            print(err)
            return {}

