import json
import requests
import time
from datetime import datetime

#The last thing that left is that chivo price has a centain 
#Delay on the Price that can be very problematics. 
#In this case is not a real problem i think for the but 
#but is good idea take it on account.
#In this case the only problem is that if worth to make it
#in that sense that has to be left tha last condition
#well i think that is the transaccion fail
host_url = 'http://diego.laptop:8085'

def timepass(timestamp, after_time):
    stamp_now = datetime.now().timestamp()
    timestamp = timestamp / 1000
    if stamp_now > timestamp + after_time:
        return True
    return False

def sellon():
    sellon_url = host_url + '/sellon'
    response = requests.get(sellon_url)
    sellon = response.json()
    return sellon['active-sellon'], float(sellon['sellon-price']), float(sellon['last-buy-stamp'])

def price_fast():
    price_url = host_url + '/set-bitstamp-price'
    response = requests.get(price_url)
    return float(response.text)

def confirm_price():
    price_url = host_url + '/real-price'
    response = requests.get(price_url)
    return float(response.text)

def buy():
    buy_url = host_url + '/buyUSD'
    response = requests.get(buy_url)

def run():
    price = None
    sellon_actice = None
    sellon_price = None
    sellon_stamp = None
    print("Start Sell On Bot") 
    while True:
        sellon_stamp, sellon_actice, sellon_price = sellon()
        price = price_fast()
        if sellon_actice:
            if price < sellon_price and timepass(sellon_price, 60*3):
                if price < confirm_price():
                    buy()
                    print("Bot sell the BTCs")
                    time.sleep(60*3)
        time.sleep(10)

if __name__ == '__main__':
    run()
