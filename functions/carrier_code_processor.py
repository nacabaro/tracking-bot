import requests
import json


def download_carrier_data():
    f = open("carrier_data.json", "wb")
    data = requests.get("https://res.17track.net/asset/carrier/info/apicarrier.all.json")
    f.write(data.content)
    f.close()
