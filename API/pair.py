import API.api_request as request
from API.candlestick import Candlestick
from API.order_book import OrderBook
from API.trade import Trade
from API.offer import Offer
import API.log as log


class Pair(object):

    def __init__(self, exchange, quote, base):
        self.exchange = exchange
        self.quote = quote
        self.base = base
        self.last_price = 0
        self.candlesticks = []
        self.candlestick_24h = None
        self.offers = []
        self.orderbook = None
        self.on_update_method = []

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
        raw_offers = request.public_request(self.exchange.get_url(), "/v2/offers", params)
        self.offers = []
        for offer in raw_offers:
            way = Trade.WAY_BUY
            quote_amount = offer["want_amount"]
            base_amount = offer["available_amount"]
            if offer["offer_asset"] == self.get_quote_token().get_name():
                way = Trade.WAY_SELL

                quote_amount = offer["available_amount"]
                base_amount = offer["want_amount"]
            quote_amount = quote_amount
            base_amount = base_amount

            price = base_amount / quote_amount

            self.offers.append(Offer(way, quote_amount, base_amount, price))
        self.orderbook = OrderBook(self, self.offers)
        log.log("pair.txt", "%s: updated" % self.get_symbol())
        self.fire_on_update()
        return self.offers

    def get_orderbook(self):
        return self.orderbook

    def get_exchange(self):
        return self.exchange

    def is_updated(self):
        return self.orderbook is not None and self.orderbook.is_updated()

    def get_equal_token(self, tp):
        if self.base == tp.get_base_token() or self.base == tp.get_quote_token():
            return self.base
        if self.quote == tp.get_quote_token() or self.quote == tp.get_base_token():
            return self.quote

    def add_on_update(self, callback):
        self.on_update_method.append(callback)

    def fire_on_update(self):
        for callback in self.on_update_method:
            callback()

    def get_candlestick_24h(self):
        return self.candlestick_24h

    def set_candlestick_24h(self, candlestick):
        self.candlestick_24h = candlestick

    def __str__(self):
        return "Pair:%s Last Price:%.8f" % (self.get_symbol(), self.get_last_price())
