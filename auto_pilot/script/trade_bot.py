
from bot_util import BotUtil

import logging
import json

logging.basicConfig(level=logging.DEBUG)


class TradeBot():
	def __init__(self):
		self.bot = BotUtil()
		pass

	def get_position(self):
		position = self.bot.get_position()
		logging.info("This is the position : "+str(position))


	def get_exec(self):
		position = self.bot.get_position()
		tradingsymbol = position['net'][0]['tradingsymbol']
		quantity = position['net'][0]['quantity']
		order_id = self.bot.excutation(quantity, tradingsymbol)
		return order_id

	def place_order(self):
		order_id = self.bot.place_order()

	def tbot(self):
		order_id = self.bot.bot()




def main():
    obj = TradeBot()
    order_id = obj.tbot()
    print(order_id)

if __name__=="__main__":
    main()
