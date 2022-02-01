from bottle import route, run, template, static_file, request
import json
from datetime import datetime
from chivo_api import Chivo
from bit_stamp_api import BitStamp

class State:
    def __init__(self):
        self.last_buy_stamp = None
        self.active_sellon = None
        self.sellon_price = None
        self.price = None
        self.state_file = "state/state.json"
        self.USD = None
        self.BTC = None
        self.load()

    def save(self):
        save_state = {
            "last_buy_stamp" : self.last_buy_stamp,
            "active-sellon" : self.active_sellon,
            "sellon-price" : self.sellon_price,
            "price" : self.price,
            "BTC" : self.BTC,
            "USD" : self.USD
        }
        with open(self.state_file, "w") as file:
            json.dump(save_state, file, indent = 2)

    def load(self):
        with open(self.state_file) as f:
            state = json.load(f)
        self.last_buy_stamp = state["last_buy_stamp"]
        self.active_sellon = state["active-sellon"]
        self.sellon_price = state["sellon-price"]
        self.price = float(state["price"])
        self.BTC = float(state["BTC"])
        self.USD = float(state["USD"])
    
    def set_last_but_stamp(self):
        self.last_buy_stamp = int(datetime.now().timestamp() * 1000)
        self.save()

    def set_price(self, new_price):
        if self.price != new_price:
            self.price = new_price
            self.save()

    def disable_sell_on(self):
        if self.active_sellon == True:
            self.active_sellon = False
            self.sellon_price = 0.0
            self.save()

    def set_sell_on(self, sellon_price):
        if sellon_price != self.sellon_price:
            self.active_sellon = True
            self.sellon_price = sellon_price
            self.save()

    def reset_sell_on(self):
        if self.active_sellon:
           self.active_sellon = False
           self.save() 

    def set_balance(self, USD, BTC):
        if not (self.USD == USD and self.BTC == BTC):
            self.USD = float(USD)
            self.BTC = float(BTC)
            self.save()
#Gobal vars
state = State()
chivo = Chivo()
bitstamp = BitStamp()
chivo.password = "000000"
chivo.auth_file = "state/diego_auth.json"
chivo.load_tokens()
chivo.refresh_tokens()
def update_balance():
    chivo.update_balance()
    state.set_balance(chivo.USD, chivo.BTC)

@route('/control/<account>')
def control_panel(account):
    if account == 'diego':
        return static_file('ControlPanel.html', root = 'pages/')
    else:
        return 'this user dont exits'

@route('/')
def ramiro_control():
    return static_file('ControlPanel.html', root = 'pages/')

@route('/css/<filename>')
def css_files(filename):
    return static_file(filename, root = 'css/')

@route('/js/<filename>')
def js_files(filename):
    return static_file(filename, root = 'js/')

@route('/price')
def price():
    return str(state.price)

@route('/real-price')
def real_price():
    state.set_price(chivo.price())
    return str(state.price)

@route('/set-bitstamp-price') 
def set_price():
    state.set_price(bitstamp.price())
    return str(state.price)

@route('/balance')
def balance():
    balance = {"USD" : state.USD, "BTC": state.BTC, "BTCUSD": state.BTC * state.price}
    return json.dumps(balance)

@route('/real-balance')
def real_balance():
    update_balance()
    balance = {"USD" : state.USD, "BTC": state.BTC, "BTCUSD": state.BTC * state.price}
    return json.dumps(balance)

@route('/sellon')
def sellon():
    sellonstate = {"last-buy-stamp" : state.last_buy_stamp,
                   "active-sellon" : state.active_sellon,
                   "sellon-price" : state.sellon_price}
    return json.dumps(sellonstate)

@route('/sellonset', method='POST')
def sellonset():
    sellon = request.json
    state.set_sell_on(sellon['sellon-price'])

@route('/sellonreset')
def sellonreset():
    state.reset_sell_on()


@route('/buyUSD')
def but_usd():
    chivo.purchase_dollars()
    chivo.update_balance()
    state.USD = chivo.BTC
    state.BTC = chivo.USD
    update_balance()
    state.set_last_but_stamp()
    if state.active_sellon:
        state.disable_sell_on()

@route('/buyBTC')
def buy_btc():
    chivo.purchase_bitcoin()
    chivo.update_balance()
    state.USD = chivo.BTC
    state.BTC = chivo.USD
    update_balance()
    state.set_last_but_stamp()

run(host='192.168.1.22', port = 8085, debug=True)
