from kiteconnect import KiteTicker
import logging
import json

from bot_util import BotUtil



logging.basicConfig(level=logging.DEBUG)
CRED_CONFIG_PATH = "D:/auto_pilot/config/cred.json"
CONFIG_PATH = "D:/auto_pilot/config/config.json"

class Stream_Date():

    def __init__(self):
        with open(CRED_CONFIG_PATH, 'r') as f:
            cred_config = json.load(f)
        self.api_key = cred_config['key'] 
        self.access_token = cred_config['access_tkn']
        self.kws=KiteTicker(self.api_key,self.access_token)

        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        self.tokens = [config['tokens']]

        self.bot = BotUtil()

    def on_ticks(self,ws,ticks):
        self.bot.set_ltp(ticks)
        for tick in ticks:
            logging.info("market price : "+str(tick['last_price']))


    def on_connect(self,ws,response):
        ws.subscribe(self.tokens)
        ws.set_mode(ws.MODE_FULL,self.tokens)


def main():
    stream_data = Stream_Date() 
    stream_data.kws.on_ticks=stream_data.on_ticks
    stream_data.kws.on_connect=stream_data.on_connect
    stream_data.kws.connect()

if __name__=="__main__":
    main()