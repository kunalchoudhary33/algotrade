from kiteconnect import KiteConnect
import logging
import json
import time

logging.getLogger("urllib3").setLevel(logging.WARNING)
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
        self.index = [config['index']]
        self.expiry = [config['expiry']]
 
        self.option = []

        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)


    def select_strike_price(self, value1, value2, value3, value4):
        value1_price = self.kite.quote('NFO:'+str(value1))['NFO:'+str(value1)]["last_price"]
        value2_price = self.kite.quote('NFO:'+str(value2))['NFO:'+str(value2)]["last_price"]
        value3_price = self.kite.quote('NFO:'+str(value3))['NFO:'+str(value3)]["last_price"]
        value4_price = self.kite.quote('NFO:'+str(value4))['NFO:'+str(value4)]["last_price"]
        diff1 = abs(value1_price - 100)
        diff2 = abs(value2_price - 100)
        diff3 = abs(value3_price - 100)
        diff4 = abs(value4_price - 100)
        min_diff = min(diff1, diff2, diff3, diff4)
        if min_diff == diff1:
            return value1
        elif min_diff == diff2:
            return value2
        elif min_diff == diff3:
            return value3
        else:
            return value4

    def strike_price(self):
        ticks = self.kite.quote('NSE:NIFTY 50')
        ltp = ticks['NSE:NIFTY 50']['last_price']
        atm = round(ltp / 50) * 50
        otm = atm - 50
        itm = atm + 50
        itm1 = atm + 50 + 50
        atm_symbol = "NIFTY23"+str(self.expiry[0])+str(atm)+self.option[0]
        otm_symbol = "NIFTY23"+str(self.expiry[0])+str(otm)+self.option[0]
        itm_symbol = "NIFTY23"+str(self.expiry[0])+str(itm)+self.option[0]
        itm1_symbol = "NIFTY23"+str(self.expiry[0])+str(itm1)+self.option[0]

        strike_price = self.select_strike_price(atm_symbol, otm_symbol, itm_symbol, itm1_symbol)
        return strike_price
    


    def place_buy_order(self):
        logging.info("Algo started to place order and execution.")
        option = input("Enter the options (CE/PE) : ")
        self.option.append(option)
        strike_price = self.strike_price()
        print("Oders executed for : "+str(strike_price))
        order_id = self.kite.place_order('regular', 'NFO', strike_price, 'BUY', self.quantity, 'NRML', 'MARKET')
        return order_id
    
    

    def get_position(self):
        tradingsymbol = ""
        buy_price = 0
        quantity = 0
        position = self.kite.positions()
        for open_position in position['net']:
            qty = open_position['quantity']
            if(qty>0):
                tradingsymbol = open_position['tradingsymbol']
                quantity = open_position['quantity']
                buy_price = open_position['last_price']
                return tradingsymbol, quantity, buy_price
            else:
                logging.info("No Open position found")
                return tradingsymbol, quantity, buy_price
    

    def auto_trade(self):
        stoploss_per = 0.89
        target_per = 1.10
        train_sl_per = 0.95
        tradingsymbol, quantity, buy_price = self.get_position()
        logging.info("tradingsymbol : "+str(tradingsymbol))
        logging.info("quantity : "+str(quantity))
        logging.info("buy_price : "+str(buy_price))

        stoploss = round(stoploss_per * buy_price)
        target = round(target_per * buy_price)
        logging.info("stoploss : "+str(stoploss))
        logging.info("target : "+str(target))

        full_qty = int(self.quantity[0])
        half_qty = int(self.quantity[0] / 2)

        trailsl = False
        max_point = 0
        while True:
            ltp = self.kite.quote('NFO:'+str(tradingsymbol))['NFO:'+str(tradingsymbol)]["last_price"] 

            if(trailsl == False):
                if(ltp <= stoploss):
                    order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', full_qty, 'NRML', 'MARKET')
                    logging.info("Stop loss hit")
                    break
                elif(ltp >= target):
                    order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', half_qty, 'NRML', 'MARKET')
                    profit = (target - stoploss) * half_qty
                    logging.info("Target Hit. Profit booked for 1st milestone. "+str(profit))

                    trailsl = True
                    max_point = ltp
                    stoploss = buy_price

            elif(trailsl == True):
                if(ltp >= max_point):
                    max_point = ltp
                    stoploss = (train_sl_per * max_point)
                    min_profit = (stoploss - buy_price) * half_qty
                    logging.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    logging.info("New Stoploss : "+str(stoploss))
                    logging.info("max_point : "+str(max_point))
                    logging.info("min_profit : "+str(min_profit))

                if(ltp <= stoploss):
                    order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', half_qty, 'NRML', 'MARKET')
                    logging.info("Trailing SL Hit")
                    break

            time.sleep(0.25)       
    



cls = Bot()
cls.place_buy_order()
cls.auto_trade()



