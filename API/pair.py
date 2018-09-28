import API.api_request as request
from API.candlestick import Candlestick

class Pair(object):

    def __init__(self, exchange, quote, base):
        self.exchange = exchange
        self.quote = quote
        self.base = base
        self.last_price = 0
        self.candlesticks = []
        self.offers = []

    def get_quote_token(self):
        return self.quote

    def get_base_token(self):
        return self.base

    def get_symbol(self):
        return self.quote.get_name()+"_"+self.base.get_name()

    def load_tickers(self, start_time, end_time, interval):
        params = {"start_time": start_time, "end_time": end_time, "interval": interval}
        raw_candles = request.public_request(self.exchange.get_url(), "/v2/tickers/candlesticks", params)
        self.candlesticks = []
        for entry in raw_candles:
            self.candlesticks.append(Candlestick(self, int(entry["time"]), float(entry["open"]),
                                            float(entry["close"]), float(entry["high"]), float(entry["low"]),
                                            float(entry["volume"]), float(entry["quote_volume"]), interval))
        return self.candlesticks

    def load_last_price(self):
        self.last_price = float(request.public_request(self.exchange.get_url(), "/v2/tickers/last_price",
                                                       {self.get_quote_token().get_name()}))
        return self.last_price

    def set_last_price(self, price):
        self.last_price = price

    def get_last_price(self):
        return self.last_price

    def load_offers(self, contract):
        params = {"blockchain": contract.get_chain().lower(), "pair": self.get_symbol(), "contract_hash": contract.get_latest_hash()}
        self.offers = request.public_request(self.exchange.get_url(), "/v2/offers", params)
        return self.offers

    def __str__(self):
        return "Pair:%s Last Price:%.8f" % (self.get_symbol(), self.get_last_price())
