def round_to_nearest_50(input_value):
    # Calculate the rounded value
    rounded_value = round(input_value / 50) * 50
    return rounded_value

# Test cases
test_cases = [20105, 20145, 20162, 20188]

for value in test_cases:
    output = round_to_nearest_50(value)
    print(f"Value: {value}, Output: {output}")


# def auto_trade_trail(self):
#         stoploss_per = 0.89
#         target_per = 1.10
#         train_sl_per = 0.95
        
#         stoploss = round(stoploss_per * buy_price)
#         target = round(target_per * buy_price)

#         tradingsymbol, quantity, buy_price = self.get_position()
#         if(buy_price < 100):
#             target = round(buy_price + 10)
#             stoploss = round(buy_price - 10)
#         else:
#             target = round(buy_price * 1.10)
#             stoploss = round(buy_price * 0.90)

#         logging.info("tradingsymbol : "+str(tradingsymbol))
#         logging.info("quantity : "+str(quantity))
#         logging.info("buy_price : "+str(buy_price))
#         logging.info("stoploss : "+str(stoploss))
#         logging.info("target : "+str(target))

#         full_qty = int(self.quantity[0])
#         half_qty = int(self.quantity[0] / 2)

#         trailsl = False
#         max_point = 0
#         while True:
#             ltp = self.kite.quote('NFO:'+str(tradingsymbol))['NFO:'+str(tradingsymbol)]["last_price"] 

#             if(trailsl == False):
#                 if(ltp <= stoploss):
#                     order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', full_qty, 'NRML', 'MARKET')
#                     logging.info("Stop loss hit")
#                     break
#                 elif(ltp >= target):
#                     order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', full_qty, 'NRML', 'MARKET')
#                     profit = (target - buy_price) * full_qty
#                     logging.info("Target Hit. Profit booked for 1st milestone. "+str(profit))
#                     break

#                     # trailsl = True
#                     # max_point = ltp
#                     # stoploss = buy_price

#             # elif(trailsl == True):
#             #     if(ltp >= max_point):
#             #         max_point = ltp
#             #         stoploss = (train_sl_per * max_point)
#             #         min_profit = (stoploss - buy_price) * half_qty
#             #         logging.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
#             #         logging.info("New Stoploss : "+str(stoploss))
#             #         logging.info("max_point : "+str(max_point))
#             #         logging.info("min_profit : "+str(min_profit))

#             #     if(ltp <= stoploss):
#             #         order_id = self.kite.place_order('regular', 'NFO', tradingsymbol, 'SELL', half_qty, 'NRML', 'MARKET')
#             #         logging.info("Trailing SL Hit")
#             #         break

#             time.sleep(0.20)       


{'net': [{'tradingsymbol': 'NIFTY2392120200PE', 'exchange': 'NFO', 'instrument_token': 13995778, 'product': 'NRML', 'quantity': 50, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 103.4, 'close_price': 0, 'last_price': 100.05, 'value': -3200, 'pnl': 1802.5, 'm2m': 1802.5, 'unrealised': 1802.5, 'realised': 0, 'buy_quantity': 600, 'buy_price': 103.4, 'buy_value': 62040, 'buy_m2m': 62040, 'sell_quantity': 550, 'sell_price': 106.98181818181818, 'sell_value': 58840, 'sell_m2m': 58840, 'day_buy_quantity': 600, 'day_buy_price': 103.4, 'day_buy_value': 62040, 'day_sell_quantity': 550, 'day_sell_price': 106.98181818181818, 'day_sell_value': 58840}, {'tradingsymbol': 'NIFTY2392120150CE', 'exchange': 'NFO', 'instrument_token': 13995010, 'product': 'NRML', 'quantity': 0, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 0, 'close_price': 0, 'last_price': 112.55, 'value': 5012.5, 'pnl': 5012.5, 'm2m': 5012.5, 'unrealised': 5012.5, 'realised': 0, 'buy_quantity': 500, 'buy_price': 115.975, 'buy_value': 57987.5, 'buy_m2m': 57987.5, 'sell_quantity': 500, 'sell_price': 126, 'sell_value': 63000, 'sell_m2m': 63000, 'day_buy_quantity': 500, 'day_buy_price': 115.975, 'day_buy_value': 57987.5, 'day_sell_quantity': 500, 'day_sell_price': 126, 'day_sell_value': 63000}], 'day': [{'tradingsymbol': 'NIFTY2392120200PE', 'exchange': 'NFO', 'instrument_token': 13995778, 'product': 'NRML', 'quantity': 50, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 103.4, 'close_price': 0, 'last_price': 100.05, 'value': -3200, 'pnl': 1802.5, 'm2m': 1802.5, 'unrealised': 1802.5, 'realised': 0, 'buy_quantity': 600, 'buy_price': 103.4, 'buy_value': 62040, 'buy_m2m': 62040, 'sell_quantity': 550, 'sell_price': 106.98181818181818, 'sell_value': 58840, 'sell_m2m': 58840, 'day_buy_quantity': 600, 'day_buy_price': 103.4, 'day_buy_value': 62040, 'day_sell_quantity': 550, 'day_sell_price': 106.98181818181818, 'day_sell_value': 58840}, {'tradingsymbol': 'NIFTY2392120150CE', 'exchange': 'NFO', 'instrument_token': 13995010, 'product': 'NRML', 'quantity': 0, 'overnight_quantity': 0, 'multiplier': 1, 'average_price': 0, 'close_price': 0, 'last_price': 112.55, 'value': 5012.5, 'pnl': 5012.5, 'm2m': 5012.5, 'unrealised': 5012.5, 'realised': 0, 'buy_quantity': 500, 'buy_price': 115.975, 'buy_value': 57987.5, 'buy_m2m': 57987.5, 'sell_quantity': 500, 'sell_price': 126, 'sell_value': 63000, 'sell_m2m': 63000, 'day_buy_quantity': 500, 'day_buy_price': 115.975, 'day_buy_value': 57987.5, 'day_sell_quantity': 500, 'day_sell_price': 126, 'day_sell_value': 63000}]}