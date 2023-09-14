from kiteconnect import KiteConnect
import logging
import json
import sys


logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "../config/config.json"
CRED_CONFIG_PATH = "../config/cred.json"




class Bot():
    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)

        self.quantity = [config['quantity']]
        self.option = [config['option']]
        self.index = [config['index']]
        self.expiry = [config['expiry']]
        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)


    def select_strike_price(self, value1, value2, value3):
        value1_price = self.kite.quote('NFO:'+str(value1))['NFO:'+str(value1)]["last_price"]
        value2_price = self.kite.quote('NFO:'+str(value2))['NFO:'+str(value2)]["last_price"]
        value3_price = self.kite.quote('NFO:'+str(value3))['NFO:'+str(value3)]["last_price"]
        diff1 = abs(value1_price - 100)
        diff2 = abs(value2_price - 100)
        diff3 = abs(value3_price - 100)
        min_diff = min(diff1, diff2, diff3)
        if min_diff == diff1:
            return value1
        elif min_diff == diff2:
            return value2
        else:
            return value3

    def strike_price(self):
        ticks = self.kite.quote('NSE:NIFTY 50')
        ltp = ticks['NSE:NIFTY 50']['last_price']
        atm = round(ltp / 50) * 50
        otm = atm - 50
        itm = atm + 50
        atm_symbol = "NIFTY239"+str(self.expiry[0])+str(atm)+self.option[0]
        otm_symbol = "NIFTY239"+str(self.expiry[0])+str(otm)+self.option[0]
        itm_symbol = "NIFTY239"+str(self.expiry[0])+str(itm)+self.option[0]

        strike_price = self.select_strike_price(atm_symbol, otm_symbol, itm_symbol)
        return strike_price
    


    def place_order(self):
        logging.info("This is in place order")
        strike_price = self.strike_price()
        order_id = self.kite.place_order('regular', 'NFO', strike_price, 'BUY', self.quantity, 'NRML', 'MARKET')

        return order_id
    



cls = Bot()
cls.place_order()