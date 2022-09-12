import requests
import json


class TrackingMore:
    def __init__(self):
        self.__secrets = None
        self.__base_url = "https://api.17track.net/track/v2"

    def set_secret(self, secret):
        self.__secrets = secret

    def add_shipping_code(self, code, carrier=None):
        if carrier is None:
            post = [{"number": code}]
        else:
            post = [{"number": code, "carrier": carrier}]

        r = requests.post(f'{self.__base_url}/register',
                          headers={'Content-Type': 'application/json', '17token': f'{self.__secrets}'},
                          data=json.dumps(post))
        return r.json()

    def get_shipping_status(self, code, carrier):
        post = [{"number": code, "carrier": carrier}]
        r = requests.post(f'{self.__base_url}/push',
                          headers={'Content-Type': 'application/json', '17token': f'{self.__secrets}'},
                          data=json.dumps(post))
        return r.json()

    def remove_shipping_code(self, code, carrier):
        post = [{"number": code, "carrier": carrier}]
        r = requests.post(f'{self.__base_url}/deletetrack',
                          headers={'Content-Type': 'application/json', '17token': f'{self.__secrets}'},
                          data=json.dumps(post))
        return r.json()
