import requests
from functools import wraps


def wait_on_429(func):
    @wraps(func)
    def wrapper_wait(self, *args, **kwargs):
        result = func(self, *args, **kwargs)

        if isinstance(result, tuple) and len(result) >= 2 and result[1] == 429:
            asyncio.sleep(10)
            result = func(self, *args, **kwargs)

        return result

    return wrapper_wait


class APIHandler:
    def __init__(self, client_id: str | None = None, client_secret: str | None = None):
        if client_id and client_secret:
            self._client_id = client_id
            self._client_secret = client_secret

    def post(self, url, headers, payload, use_secret: bool = False, **kwargs) -> tuple[dict, int]:
        if use_secret and self._client_id and self._client_secret:
            payload['client_id'] = self._client_id
            payload['client_secret'] = self._client_secret

        if kwargs:
            payload.update(kwargs)

        try:
            response = requests.post(url=url, headers=headers, data=payload)

            try:
                return response.json(), response.status_code
            except requests.exceptions.JSONDecodeError as err:
                return {
                    'response': response.text
                }, response.status_code
        except requests.exceptions.ConnectionError as err:
            return {}, 503

    @staticmethod
    def get(url, **kwargs) -> tuple[dict, int]:
        try:
            async with requests.Session() as session:
                request = requests.Request('GET', url=url, **kwargs)
                prepped = session.prepare_request(request)

                if prepped.headers:
                    # prepped.headers = prepped.headers
                    print(prepped.headers)

                response = session.send(prepped)

            try:
                return response.json(), response.status_code
            except requests.exceptions.JSONDecodeError as err:
                return {
                    'response': response.text
                }, response.status_code
        except requests.exceptions.ConnectionError as err:
            return {}, 503


if __name__ == '__main__':
    api = APIHandler()
    api.get(url='http://127.0.0.1:5000/api/v1/autocomplete?q=Come', headers={'Authorization': 'Bearer  123'})

