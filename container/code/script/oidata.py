import os
import copy
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
import time
import dateutil.parser
import threading
import sys
from datetime import datetime, timedelta
import logging
import json

from database import Database

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
CONFIG_PATH = "../config/config.json"
CRED_CONFIG_PATH = "../config/cred.json"


class Oidata():
    def __init__(self):
        self.db = Database()

        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']

        self.kite = KiteConnect(api_key=self.api_key)
        self.kite.set_access_token(access_token=self.access_token)

        self.oc_symbol = "NIFTY"
        # self.oc_expiry = "25-01-2024"

        self.pre_oc_symbol = ""
        self.pre_oc_expiry = ""
        self.expiries_list = []
        # self.instrument_dict = {}
        self.prev_day_oi = {}
        self.stop_thread = False
        self.exchange = None

        try:
            self.kite.margins()
        except:
            print("Login Failed!!!!")
            sys.exit()


    def get_exchange(self):
        # exchange = None
        while True:
            if self.exchange is None:
                try:
                    self.exchange = pd.DataFrame(self.kite.instruments("NFO"))
                    self.exchange = self.exchange[self.exchange["segment"] == "NFO-OPT"]
                    break
                except:
                    print("Exchange Download Error...")
                    time.sleep(10)

        df = pd.DataFrame({"FNO Symbol": list(self.exchange["name"].unique())})
        df = df.set_index("FNO Symbol", drop=True)



    def get_oi(self, data):
        # global prev_day_oi, kite, stop_thread
        for symbol, v in data.items():
            if self.stop_thread:
                break
            while True:
                try:
                    self.prev_day_oi[symbol]
                    break
                except:
                    try:
                        pre_day_data = self.kite.historical_data(v["token"], (datetime.now() - timedelta(days=5)).date(),
                                            (datetime.now() - timedelta(days=1)).date(), "day", oi=True)
                        try:
                            self.prev_day_oi[symbol] = pre_day_data[-1]["oi"]
                        except:
                            self.prev_day_oi[symbol] = 0
                        break
                    except Exception as e:
                        time.sleep(0.5)


    def formatINR(self,number):
        number = float(number)
        number = round(number,2)
        is_negative = number < 0
        number = abs(number)
        s, *d = str(number).partition(".")
        r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
        value = "".join([r] + d)
        if is_negative:
            value = '-' + value
        return value

    def main(self):
        self.get_exchange()
        print("Data loading started...")
        prev_ce_value = 0
        prev_pe_value = 0
        while True:

            # oc_symbol = "NIFTY"
            oc_expiry = "25-01-2024"
            oc_expiry = datetime.strptime(oc_expiry, "%d-%m-%Y")
            if self.pre_oc_symbol != self.oc_symbol or self.pre_oc_expiry != oc_expiry:

                instrument_dict = {}
                self.stop_thread = True
                time.sleep(2)
                if self.pre_oc_symbol != self.oc_symbol:

                    self.expiries_list = []
                self.pre_oc_symbol = self.oc_symbol
                self.pre_oc_expiry = oc_expiry

            if self.oc_symbol is not None:
                try:
                    if not self.expiries_list:
                        df = copy.deepcopy(self.exchange)
                        df = df[df["name"] == self.oc_symbol]
                        self.expiries_list = sorted(list(df["expiry"].unique()))
                        df = pd.DataFrame({"Expiry Date": self.expiries_list})
                        df = df.set_index("Expiry Date", drop=True)

                    if not instrument_dict and oc_expiry is not None:
                        df = copy.deepcopy(self.exchange)
                        df = df[df["name"] == self.oc_symbol]
                        df = df[df["expiry"] == oc_expiry.date()]
                        lot_size = list(df["lot_size"])[0]
                        for i in df.index:
                            instrument_dict[f'NFO:{df["tradingsymbol"][i]}'] = {"strikePrice": float(df["strike"][i]),
                                                                                "instrumentType": df["instrument_type"][i],
                                                                                "token": df["instrument_token"][i]}
                        self.stop_thread = False
                        thread = threading.Thread(target=self.get_oi, args=(instrument_dict,))
                        thread.start()
                    option_data = {}
                    instrument_for_ltp = "NSE:NIFTY 50" if self.oc_symbol == "NIFTY" else (
                                        "NSE:NIFTY BANK" if self.oc_symbol == "BANKNIFTY" else ("NSE:NIFTY FIN SERVICE" if self.oc_symbol == "FINNIFTY" else f"NSE:{self.oc_symbol}"))
                    underlying_price = kite.quote(instrument_for_ltp)[instrument_for_ltp]["last_price"]
                    for symbol, values in kite.quote(list(instrument_dict.keys())).items():
                        try:
                            try:
                                option_data[symbol]
                            except:
                                option_data[symbol] = {}
                            option_data[symbol]["strikePrice"] = instrument_dict[symbol]["strikePrice"]
                            option_data[symbol]["instrumentType"] = instrument_dict[symbol]["instrumentType"]
                            option_data[symbol]["lastPrice"] = values["last_price"]
                            option_data[symbol]["totalTradedVolume"] = values["volume"]
                            option_data[symbol]["openInterest"] = int(values["oi"]/lot_size)
                            option_data[symbol]["change"] = values["last_price"] - values["ohlc"]["close"] if values["last_price"] != 0 else 0
                            try:
                                option_data[symbol]["changeinOpenInterest"] = int((values["oi"] - self.prev_day_oi[symbol])) #/lot_size)
                            except:
                                option_data[symbol]["changeinOpenInterest"] = None

                        except Exception as e:
                            pass

                    df = pd.DataFrame(option_data).transpose()
                    ce_df = df[df["instrumentType"] == "CE"]
                    ce_df = ce_df[["totalTradedVolume", "change", "lastPrice", "changeinOpenInterest", "openInterest", "strikePrice"]]
                    ce_df = ce_df.rename(columns={"openInterest": "CE OI", "changeinOpenInterest": "CE Change in OI",
                                                "lastPrice": "CE LTP", "change": "CE LTP Change", "totalTradedVolume": "CE Volume"})
                    ce_df.index = ce_df["strikePrice"]
                    ce_df = ce_df.drop(["strikePrice"], axis=1)
                    ce_df["Strike"] = ce_df.index
                    pe_df = df[df["instrumentType"] == "PE"]
                    pe_df = pe_df[["strikePrice", "openInterest", "changeinOpenInterest",  "lastPrice", "change", "totalTradedVolume"]]
                    pe_df = pe_df.rename(columns={"openInterest": "PE OI", "changeinOpenInterest": "PE Change in OI",
                                                "lastPrice": "PE LTP", "change": "PE LTP Change", "totalTradedVolume": "PE Volume"})
                    pe_df.index = pe_df["strikePrice"]
                    pe_df = pe_df.drop("strikePrice", axis=1)
                    df = pd.concat([ce_df, pe_df], axis=1).sort_index()
                    df = df.replace(np.nan, 0)
                    df["Strike"] = df.index
                    df.index = [np.nan] * len(df)

                    atm_strike = round(underlying_price / 50) * 50
                    strike_prices = [atm_strike-250, atm_strike-200, atm_strike-150, atm_strike-100,  atm_strike-50, atm_strike, atm_strike+50, atm_strike+100, atm_strike+150, atm_strike+200, atm_strike+250]
                    selected_rows = df[df['Strike'].isin(strike_prices)]
                    df_new = pd.DataFrame(selected_rows)

                    print(df_new.head())
                    sum_of_chng_oi_ce = df_new["CE Change in OI"].sum()
                    sum_of_chng_oi_pe = df_new["PE Change in OI"].sum()
                    if(prev_ce_value != sum_of_chng_oi_ce or prev_pe_value != sum_of_chng_oi_pe):
                        prev_ce_value = sum_of_chng_oi_ce
                        prev_pe_value = sum_of_chng_oi_pe
                        local_df = pd.DataFrame()
                        local_data = {'CE Sellers' : [self.formatINR(sum_of_chng_oi_ce)],'Diff' : [self.formatINR(sum_of_chng_oi_pe - sum_of_chng_oi_ce)] ,'PE Selleres' :  [self.formatINR(sum_of_chng_oi_pe)]}
                        local_df = pd.DataFrame(local_data)
                        db.insert_data(datetime.now(),sum_of_chng_oi_pe - sum_of_chng_oi_ce)
                        print(local_df.head())
                        print(" ")  
                    time.sleep(5)

                except Exception as e:
                    pass




oi = Oidata()
oi.main()




