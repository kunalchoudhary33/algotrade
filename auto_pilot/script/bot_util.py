import sqlite3
import pandas as pd
import datetime
from kiteconnect import KiteTicker
from kiteconnect import KiteConnect
import logging
import json
import sys

logging.basicConfig(level=logging.DEBUG)

CONFIG_PATH = "D:/auto_pilot/config/config.json"
PRICE_CONFIG_PATH = "D:/auto_pilot/config/price_config.json"
CRED_CONFIG_PATH = "D:/auto_pilot/config/cred.json"

last_traded_price = 0

class BotUtil():
    
    def __init__(self):
        self.ltp = 0
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = [config['tokens']]
        self.trading_symbol = [config['trading_symbol']]
        

        self.target = [config['target']]
        self.stop_loss = [config['stop_loss']]
        self.option = [config['option']]
        self.index = [config['index']]
        self.lot_size = [config['lot_size']]
        self.spare_lot_size = [config['spare_lot_size']]
        self.expiry = [config['expiry']]
        self.buy_price = 0

        
        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)
    
            

    def get_ltp(self):
        return last_traded_price
        

    def set_ltp(self, ticks):
        for tick in ticks:
            self.ltp = tick['last_price']
    
        dict_cred = {
            'ltp' : self.ltp
        }
        price_object = json.dumps(dict_cred, indent = 1)
        with open(PRICE_CONFIG_PATH, "w") as outfile:
            outfile.write(price_object)



    def get_position(self):
        self.position = self.kite.positions()
        for open_position in self.position['net']:
            quantity = open_position['quantity']
            if(quantity>0):
                self.tradingsymbol = open_position['tradingsymbol']
                self.quantity = open_position['quantity']
        return self.position


    def excutation(self, qnty):
        instrument_symbol = self.tradingsymbol
        order_id = self.kite.place_order('regular', 'NFO', instrument_symbol, 'SELL', qnty, 'NRML', 'MARKET')
        return order_id

    def ce_bot(self):
        is_spare_quantity_booked = False
        is_half_stop_loss_moved = False
        is_quarter_stop_loss_moved = False
        order_id = 0
        count = 0
        
        
        target_price = self.buy_price + self.target[0]
        stop_loss_price = self.buy_price - self.stop_loss[0]
        spare_target = self.buy_price + self.stop_loss[0]
        half_stop_loss_price = self.buy_price - (self.stop_loss[0] / 2)
        quarter_target = self.buy_price + (0.75 * self.target[0])

        logging.info("entry price : "+str(self.buy_price))
        logging.info("target : "+str(target_price))
        logging.info("stop loss : "+str(stop_loss_price))
        logging.info("spare target : "+str(spare_target))
        logging.info("quarter target : "+str(quarter_target))
        
        if(self.index[0]=="NIFTY BANK"):
            spare_quantity = self.spare_lot_size[0] * 25
        if(self.index[0]=="NIFTY 50"):
            spare_quantity = self.spare_lot_size[0] * 50

        for i in range(sys.maxsize**10):
            count = count + 1
            try:
                with open(PRICE_CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                last_traded_price = [config['ltp']][0]
            except:
                pass


            if(is_half_stop_loss_moved == False and last_traded_price>=spare_target):
                self.get_position()
                #order_id = self.excutation(spare_quantity)
                logging.info("Spare Quantity booked. Total lot booked :  "+str(self.spare_lot_size))
                stop_loss_price = half_stop_loss_price
                is_half_stop_loss_moved = True
                logging.info("Stop loss reduced to half. New Stoploss : "+str(stop_loss_price))
        
            if(is_quarter_stop_loss_moved == False and last_traded_price>=quarter_target):
                stop_loss_price = self.buy_price
                is_quarter_stop_loss_moved = True
                logging.info("Stop loss at entry price. New Stoploss : "+str(stop_loss_price))

            if(last_traded_price>=target_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the target")
                break

            if(last_traded_price < stop_loss_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the stop loss")
                break

        return order_id


    def pe_bot(self):
        is_spare_quantity_booked = False
        is_half_stop_loss_moved = False
        is_quarter_stop_loss_moved = False
        order_id = 0
        count = 0
        
        target_price = self.buy_price - self.target[0]
        stop_loss_price = self.buy_price + self.stop_loss[0]
        spare_target = self.buy_price - self.stop_loss[0]
        half_stop_loss_price = self.buy_price + (self.stop_loss[0] / 2)
        quarter_target = self.buy_price - (0.75 * self.target[0])

        logging.info("entry price : "+str(self.buy_price))
        logging.info("target : "+str(target_price))
        logging.info("stop loss : "+str(stop_loss_price))
        logging.info("spare target : "+str(spare_target))
        logging.info("quarter target : "+str(quarter_target))

        if(self.index[0]=="NIFTY BANK"):
            spare_quantity = self.spare_lot_size[0] * 25
        if(self.index[0]=="NIFTY 50"):
            spare_quantity = self.spare_lot_size[0] * 50

        for i in range(sys.maxsize**10):
            count = count + 1
            try:
                with open(PRICE_CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                last_traded_price = [config['ltp']][0]
            except:
                pass


            if(is_half_stop_loss_moved == False and last_traded_price<=spare_target):
                self.get_position()
                #order_id = self.excutation(spare_quantity)
                logging.info("Spare Quantity booked. Total lot booked :  "+str(self.spare_lot_size))
                stop_loss_price = half_stop_loss_price
                is_half_stop_loss_moved = True
                logging.info("Stop loss reduced to half. New Stoploss : "+str(stop_loss_price))
        
            if(is_quarter_stop_loss_moved == False and last_traded_price<=quarter_target):    
                stop_loss_price = self.buy_price
                is_quarter_stop_loss_moved = True
                logging.info("Stop loss at entry price. New Stoploss : "+str(stop_loss_price))

            if(last_traded_price<=target_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the target")
                break

            if(last_traded_price > stop_loss_price):
                self.get_position()
                order_id = self.excutation(self.quantity)
                logging.info("Price hit the stop loss")
                break

        return order_id


    def fetch_instrument(self):
        if(self.index[0]=="NIFTY BANK"):
            ticks = self.kite.quote('NSE:NIFTY BANK')
            ltp = ticks['NSE:NIFTY BANK']['last_price']
            if(self.option[0]=="CE"):
                instrument_symbol = "BANKNIFTY233"+str(self.expiry[0])+str(int(str(ltp)[:3]) - 1)+"00"+self.option[0]
            if(self.option[0]=="PE"):
                instrument_symbol = "BANKNIFTY233"+str(self.expiry[0])+str(int(str(ltp)[:3]) + 3)+"00"+self.option[0]
            quantity = self.lot_size[0] * 25
        if(self.index=="NIFTY 50"):
            ticks = self.kite.quote('NSE:NIFTY 50')
            ltp = ticks['NSE:NIFTY 50']['last_price']
            instrument_symbol = "NIFTY233"+str(self.expiry[0])+str(str(ltp)[:3])+"00"+self.option[0]
            quantity = self.lot_size[0] * 50
        return quantity, instrument_symbol
    


    def place_order(self):
        try:
            quantity, instrument_symbol = self.fetch_instrument()
            order_id = self.kite.place_order('regular', 'NFO', instrument_symbol, 'BUY', quantity, 'NRML', 'MARKET')
            try:
                with open(PRICE_CONFIG_PATH, 'r') as f:
                    config = json.load(f)
                self.buy_price = [config['ltp']][0]
            except:
                pass
            logging.info("############################# Order Placed ##########################################")
            logging.info("Order placed. ID is: {}".format(order_id))
        except Exception as e:
            logging.info("Order placement failed: {}".format(e.message))
        self.kite.orders()
        self.kite.instruments()
        return order_id


    def bot(self):
        order = input("Press y to place order : ")
        if(order=='y'):
            self.place_order()
        logging.info("###########  AUTO PILOT MODE ON  ####################")
        logging.info("Option trading in : "+str(self.option[0]))
        if(self.option[0]=="CE"):
            self.ce_bot()
        elif(self.option[0]=="PE"):
            self.pe_bot()