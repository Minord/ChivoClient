
import requests
import time
from datetime import datetime

price_file = 'state/price_record.csv'
bitstamp_price_file = 'state/bitstamp_price_record.csv'
host_url = 'http://localhost:8080'

#How to make that in this case the python works
#Good for making this thing work well
#firts we firts have to solve the cuestion of frecency
#then make other workings.

#Chivo Signal
#Bit Stamp Signal

#Assumptions

#Chivo update on regular interval of time
#What is the description of thar interval
#Chivo has a delay with the BitStamp
#Signal and seams quite hard to understand what we
#shoul make work
#The hard part on the thing is making 

def run():
    start = None
    offset = None
    interval = None
    delay = None

    discovery_mode = True
    rediscover_mode = False

    while True:
    if discovery_mode == False and rediscover_mode == False:
    #Normal working
        if istime:
            web.setBitStampPrice()
        if expiredInterval:
            rediscover_mode = False

    elif rediscover_mode:
        #Rediscover Mode
    elif discovery_mode:
        #Discover mode



if __name__ == '__main__':
    run()
