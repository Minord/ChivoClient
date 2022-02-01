import requests
import json

import logging

from datetime import datetime

auth_file = "auth.json"

#Function for truncate numbers
def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def try_json(text):
    result = ""
    try:
        json_result = json.loads(text)
        result = json.dumps(json_result, indent = 2)
    except ValueError as e:
        result = text
    return result

#Price Source
class Chivo(): 
    def __init__(self,
                 access_token = None,
                 refesh_token = None,
                 auth_file = None,
                 balance_file = None,
                 password = None):

        self.access_token = access_token
        self.refresh_token = refesh_token
        self.user_name = "No body"
        self.auth_file = auth_file
        self.balance_file = balance_file
        self.BTC = 0.0
        self.USD = 0.0
        self.purchase_price = 0.0
        self.password = password

    #Data Consult Methods        
    def price(self):
        url = "https://app.chivowallet.com/api/v1/rate/1/BTC/USD/"
        response = requests.get(url, headers = self.headers())

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
        	#Try again
        	logging.info('Not valid tokens try recover')
        	return self.price()
        total = json_result["total"]

        logging.info(f'Consult chivo price {total}')
        logging.info(try_json(response.text))

        return float(total)

    def get_user_name(self):
        url = "https://app.chivowallet.com/api/v1/users/"
        response = requests.get(url, headers = self.headers())

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
        	#Try again
        	return self.get_user_name()

        self.user_name = json_result["user_info"]["first_name"]
        logging.info('The user is call [{self.user_name}]')

        return self.user_name

    def update_balance(self, show = False):
        url = "https://app.chivowallet.com/api/v1/balances/"
        response = requests.get(url, headers = self.headers())

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
        	#try again
        	return self.update_balance()

        logging.info(try_json(response.text))
        portfolio = json_result
        self.USD = portfolio["data"][0]["amount"]
        self.BTC = portfolio["data"][1]["amount"]

        logging.info(f'The balance was updated the balance is {self.USD}USD and {self.BTC}BTC')


	#Convertion API    
    def prepare_dollars_purchase(self):
        btc_amount = truncate(self.BTC, 8)
        uds_amount = truncate(float(btc_amount) * self.purchase_price , 2)

        url = "https://app.chivowallet.com/api/v1/refill/available/currencies/"+uds_amount+"/?pay="+btc_amount
        response = requests.get(url, headers = self.headers())

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
        	#try again
        	return self.prepare_dollars_purchase()

        logging.info('Preparing dollars purchase')
        logging.info(f'url : {url}')
        logging.info(f'response : {response.text}')
        logging.info(f'Original BTC amount : {truncate(float(btc_amount) * self.purchase_price, 16)}')

    
    def make_dollars_purchase(self, show = False):
        url = "https://app.chivowallet.com/api/v1/refill/purchase/"
                              
        purchase_data = {"amount" : truncate(float(self.BTC) * self.purchase_price, 2),
                         "currency": "BTC",
                         "exchange_id": 11}
        
        logging.info(purchase_data)

        purchase_data = json.dumps(purchase_data)
        response = requests.post(url, headers = self.headers(), data = purchase_data)

        logging.info(try_json(response.text))
    
    def purchase_dollars(self, show = False):
        self.update_balance()
        self.purchase_price = self.price()
        self.prepare_dollars_purchase()
        self.validate_password()
        self.make_dollars_purchase(show = show)
    
    def prepare_bitcoin_purchase(self):
        uds_amount = truncate(self.USD, 2)
        btc_amount = truncate(float(uds_amount) / self.purchase_price , 8)
                              
        url = "https://app.chivowallet.com/api/v1/crypto/available/currencies/"+btc_amount+"/?pay="+uds_amount
        response = requests.get(url, headers = self.headers())

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
        	#try again
        	return self.prepare_dollars_purchase()
                              
       	logging.info("Original BTC amount : " + truncate(float(uds_amount) / self.purchase_price , 16))
        logging.info(url)
        logging.info(try_json(response.text))
    
    def make_bitcoin_purchase(self, show = False):
        purchase_data = {"amount" : truncate(self.USD / self.purchase_price, 8),
                         "currency": "USD",
                         "exchange_id": 11}

        logging.info(purchase_data)

        url = "https://app.chivowallet.com/api/v1/crypto/purchase/"
        purchase_data = json.dumps(purchase_data)
        response = requests.post(url, headers = self.headers(), data = purchase_data)

        logging.info(try_json(response.text))
    
    def purchase_bitcoin(self, show = False):
        self.update_balance()
        self.purchase_price = self.price()
        self.prepare_bitcoin_purchase()
        self.validate_password()
        self.make_bitcoin_purchase(show = show)

    def validate_password(self):
        url = 'https://app.chivowallet.com/api/v1/commerce/check/pin/' 
        password_data = {"password" : self.password}
        password_data = json.dumps(password_data)

        response = requests.post(url, headers = self.headers(), data = password_data)

        json_result, valid_tokens = self.response_recover_tokens(response)

        if not valid_tokens:
            #try again
            return self.validate_password()






    #Auth methods
    def obtain_tokens(self, code, dui = None, phone = None, password = None):
        if not phone:
            phone = "Somephone"
        if not dui:
            dui = "somedui"
        if not password:
            password = "code"
            
        credentials = {"phone_number": phone,
                       "code": code,
                       "dni": dui,
                       "password" : password}
        
        credentials = json.dumps(credentials)

        get_token_url =  "https://app.chivowallet.com/api/v1/auth/token/obtain/"
        response = requests.post(get_token_url, headers = self.headers(), data = credentials)
        
        logging.info(credentials)
        logging.info(try_json(response.text))
                        
        tokens  = json.loads(response.text)
        self.access_token  = tokens["access"]
        self.refresh_token = tokens["refresh"]
        self.get_user_name()

    def refresh_tokens(self):
        credential = {"refresh" : self.refresh_token}
        credential = json.dumps(credential)
        refresh_url = "https://app.chivowallet.com/api/v1/auth/token/refresh/"
        response = requests.post(refresh_url,
                                 headers = self.headers(),
                                 data = credential)

        logging.info(try_json(response.text))

        tokens = json.loads(response.text)
        self.access_token  = tokens["access"]
        self.refresh_token = tokens["refresh"]

    def save_tokens(self):

    	data = {"access" : self.access_token,
    			"refresh" : self.refresh_token}

    	with open(self.auth_file, "w") as file:
    		json.dump(data, file, indent = 2)

    	logging.info("Auth key was saved")

    def load_tokens(self):
    	with open(self.auth_file) as f:
        	auth = json.load(f)
    	self.access_token = auth["access"]
    	self.refresh_token = auth["refresh"]

    	logging.info("Tokens was loaded from file")
    
    
    def get_tokens(self, show = False):
        logging.info("access : " + str(self.access_token))
        logging.info("refesh : " + str(self.refresh_token))
        return self.access_token, self.refresh_token
    
    def set_tokens(self, tokens):
        self.access_token, self.refresh_token = tokens
        self.refresh_tokens()
        self.get_user_name()

    def response_recover_tokens(self, response):
        try:
            json_result = json.loads(response.text)
            logging.info(f'json {json_result}')
        except:
            logging.info(f'Not Json Result')
            logging.info(url)
            logging.info(response.request.headers)
            logging.info(response.text)

        if "code" in json_result:
            if json_result["code"] == "token_not_valid":
                self.refresh_tokens()
                self.save_tokens()
                logging.info("Token Updated")
                logging.info("access : "  + str(self.access_token))
                logging.info("refresh : " + str(self.refresh_token))
                return json_result, False
        return json_result, True


    #Utils Methods no API interaction

    def register_balance(self):
    	with open(self.balance_file, 'a') as file:
    		# Getting the current date and time
            dt = datetime.now()
            time = datetime.timestamp(dt)
            total = self.USD + self.BTC_on_USD()
            file.write(f'{time}, {total}, {self.USD}, {self.BTC}\n')
            logging.info('register a balance')


    def actual_currency(self):
        logging.info("Check hold currency")
        #self.update_balance()
        if(self.USD > elf.BTC_on_USD()):
            logging.info("We have USD")
            return "USD"
        elif (self.USD < self.BTC_on_USD()):
            logging.info("Whe have BTC")
            return "BTC"
        
    def BTC_on_USD(self):
    	return self.BTC * self.purchase_price
    
    def headers(self):
        headers = {"user-agent": "okhttp/3.14.9",
                   "content-type": "application/json"}
        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token
        logging.info("Headers")
        logging.info(headers)
        return headers
    
