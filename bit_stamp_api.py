import requests
import json


#Class for access bitstamp ticker
class BitStamp():
    def __init__(self, debug = False):
        self.debug = debug
    
    def price(self):
        url = "https://www.bitstamp.net/api/v2/ticker/btcusd"
        response = requests.get(url)
        response = json.loads(response.text)
        if self.debug:
            print(json.dumps(response, indent = 2))
        return float(response["last"])
