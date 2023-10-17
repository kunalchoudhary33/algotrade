import os
import copy
# import xlwings as xw
import pandas as pd
import numpy as np
from kiteconnect import KiteConnect
import time
import dateutil.parser
import threading
import sys


# from py_vollib.black_scholes.implied_volatility import implied_volatility
# from py_vollib.black_scholes.greeks.analytical import delta, gamma, rho, theta, vega
from datetime import datetime, timedelta

print("Subscribe 'TradeViaPython' YouTube")
print("----Option Chain----")
# from kite_trade import *
# enctoken = input("EncToken : ").strip()
# kite = KiteApp(enctoken=enctoken)


import logging
import json
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(level=logging.DEBUG)
CONFIG_PATH = "../config/config.json"
CRED_CONFIG_PATH = "../config/cred.json"


with open(CRED_CONFIG_PATH, 'r') as f:
    cred_config = json.load(f)
api_key = cred_config['key'] 
access_token = cred_config['access_tkn']

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token=access_token)

try:
    kite.margins()
except:
    print("Login Failed!!!!")
    sys.exit()

# if not os.path.exists("TA Python.xlsx"):
#     try:
#         wb = xw.Book()
#         wb.sheets.add("OptionChain")
#         wb.save("TA Python.xlsx")
#         wb.close()
#     except Exception as e:
#         print(f"Error Creating Excel File : {e}")
#         sys.exit()
# wb = xw.Book("TA Python.xlsx")
# oc = wb.sheets("OptionChain")
# oc.range("a:b").value = oc.range("d6:e20").value = oc.range("g1:v4000").value = None

exchange = None
while True:
    if exchange is None:
        try:
            exchange = pd.DataFrame(kite.instruments("NFO"))
            exchange = exchange[exchange["segment"] == "NFO-OPT"]
            break
        except:
            print("Exchange Download Error...")
            time.sleep(10)

df = pd.DataFrame({"FNO Symbol": list(exchange["name"].unique())})
df = df.set_index("FNO Symbol", drop=True)
# oc.range("a1").value = df

# oc.range("d2").value, oc.range("d3").value = "Symbol==>>", "Expiry==>>"

pre_oc_symbol = pre_oc_expiry = ""
expiries_list = []
instrument_dict = {}
prev_day_oi = {}
stop_thread = False


def get_oi(data):
    global prev_day_oi, kite, stop_thread
    for symbol, v in data.items():
        if stop_thread:
            break
        while True:
            try:
                prev_day_oi[symbol]
                break
            except:
                try:
                    pre_day_data = kite.historical_data(v["token"], (datetime.now() - timedelta(days=5)).date(),
                                          (datetime.now() - timedelta(days=1)).date(), "day", oi=True)
                    try:
                        prev_day_oi[symbol] = pre_day_data[-1]["oi"]
                    except:
                        prev_day_oi[symbol] = 0
                    break
                except Exception as e:
                    time.sleep(0.5)


print("Excel : Started")
while True:
    # oc_symbol, oc_expiry = oc.range("e2").value, oc.range("e3").value
    oc_symbol = "NIFTY"
    oc_expiry = "09-10-2023"
    if pre_oc_symbol != oc_symbol or pre_oc_expiry != oc_expiry:
        # oc.range("g:v").value = None
        instrument_dict = {}
        stop_thread = True
        time.sleep(2)
        if pre_oc_symbol != oc_symbol:
            # oc.range("b:b").value = oc.range("d6:e20").value = None
            expiries_list = []
        pre_oc_symbol = oc_symbol
        pre_oc_expiry = oc_expiry
    if oc_symbol is not None:
        try:
            if not expiries_list:
                df = copy.deepcopy(exchange)
                df = df[df["name"] == oc_symbol]
                expiries_list = sorted(list(df["expiry"].unique()))
                df = pd.DataFrame({"Expiry Date": expiries_list})
                df = df.set_index("Expiry Date", drop=True)
                # oc.range("b1").value = df
            if not instrument_dict and oc_expiry is not None:
                df = copy.deepcopy(exchange)
                df = df[df["name"] == oc_symbol]
                df = df[df["expiry"] == oc_expiry.date()]
                lot_size = list(df["lot_size"])[0]
                for i in df.index:
                    instrument_dict[f'NFO:{df["tradingsymbol"][i]}'] = {"strikePrice": float(df["strike"][i]),
                                                                        "instrumentType": df["instrument_type"][i],
                                                                        "token": df["instrument_token"][i]}
                stop_thread = False
                thread = threading.Thread(target=get_oi, args=(instrument_dict,))
                thread.start()
            option_data = {}
            instrument_for_ltp = "NSE:NIFTY 50" if oc_symbol == "NIFTY" else (
                                "NSE:NIFTY BANK" if oc_symbol == "BANKNIFTY" else ("NSE:NIFTY FIN SERVICE" if oc_symbol == "FINNIFTY" else f"NSE:{oc_symbol}"))
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
                        option_data[symbol]["changeinOpenInterest"] = int((values["oi"] - prev_day_oi[symbol])/lot_size)
                    except:
                        option_data[symbol]["changeinOpenInterest"] = None

                    # def greeks(premium, expiry, asset_price, strike_price, intrest_rate, instrument_type):
                    #     try:
                    #         t = ((datetime(expiry.year, expiry.month, expiry.day, 15, 30) - datetime.now()) / timedelta(
                    #             days=1)) / 365
                    #         S = asset_price
                    #         K = strike_price
                    #         r = intrest_rate
                    #         if premium == 0 or t <= 0 or S <= 0 or K <= 0 or r <= 0:
                    #             raise Exception
                    #         flag = instrument_type[0].lower()
                    #         imp_v = implied_volatility(premium, S, K, t, r, flag)
                    #         return {"IV": imp_v,
                    #                 "Delta": delta(flag, S, K, t, r, imp_v),
                    #                 "Gamma": gamma(flag, S, K, t, r, imp_v),
                    #                 "Rho": rho(flag, S, K, t, r, imp_v),
                    #                 "Theta": theta(flag, S, K, t, r, imp_v),
                    #                 "Vega": vega(flag, S, K, t, r, imp_v)}
                    #     except:
                    #         return {"IV": 0,
                    #                 "Delta": 0,
                    #                 "Gamma": 0,
                    #                 "Rho": 0,
                    #                 "Theta": 0,
                    #                 "Vega": 0}

                    # greek = greeks(values["last_price"],
                    #                oc_expiry.date(),
                    #                underlying_price,
                    #                instrument_dict[symbol]["strikePrice"],
                    #                0.1,
                    #                instrument_dict[symbol]["instrumentType"])
                    # option_data[symbol]["impliedVolatility"] = greek["IV"]
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
            print(df.head())

            # oc.range("d6").value = [["Spot LTP", underlying_price],
            #                         ["Total Call OI", sum(list(df["CE OI"]))],
            #                         ["Total Put OI", sum(list(df["PE OI"]))],
            #                         ["Total Call Change in OI", sum(list(df["CE Change in OI"]))],
            #                         ["Total Put Change in OI", sum(list(df["PE Change in OI"]))],
            #                         ["",""],
            #                         ["Max Call OI", max(list(df["CE OI"]))],
            #                         ["Max Put OI", max(list(df["PE OI"]))],
            #                         ["Max Call OI Strike", list(df[df["CE OI"] == max(list(df["CE OI"]))]["Strike"])[0]],
            #                         ["Max Put OI Strike", list(df[df["PE OI"] == max(list(df["PE OI"]))]["Strike"])[0]],
            #                         ["",""],
            #                         ["Max Call Change in OI", max(list(df["CE Change in OI"]))],
            #                         ["Max Put Change in OI", max(list(df["PE Change in OI"]))],
            #                         ["Max Call Change in OI Strike",
            #                          list(df[df["CE Change in OI"] == max(list(df["CE Change in OI"]))]["Strike"])[0]],
            #                         ["Max Put Change in OI Strike",
            #                          list(df[df["PE Change in OI"] == max(list(df["PE Change in OI"]))]["Strike"])[0]],
            #                         ]
            # oc.range("g1").value = df
        except Exception as e:
            pass




