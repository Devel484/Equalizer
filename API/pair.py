"""
author: Devel484
"""
import API.api_request as request
from API.candlestick import Candlestick
from API.order_book import OrderBook
from API.trade import Trade
from API.offer import Offer
import API.log as log


class Pair(object):

    def __init__(self, exchange, quote, base):
        """
        Trading Pair
        :param exchange: reference to the exchange(at the moment only switcheo)
        :param quote: quote token
        :param base: base token
        """
        self.exchange = exchange
        self.quote = quote
        self.base = base
        self.last_price = 0
        self.candlesticks = []
        self.candlestick_24h = None
        self.offers = []
        self.orderbook = None
        self.updating = False
        self.on_update_method = []
        self.block = False

    def is_blocked(self):
        """
        If pair is used for actual arbitrage, it is blocked for other trades
        :return: true if blocked
        """
        return self.block

    def set_blocked(self, b):
        """
        Set blocked used for trading, release after usage,
        :param b: state
        :return: None
        """
        self.block = b

    def is_updating(self):
        """
        If pair is updating offer book it returns true.
        :return: true if updating
        """
        return self.updating

    def set_updating(self, b):
        """
        Set pair is updating while loading offers.
        :param b: state
        :return: None
        """
        self.updating = b

    def get_quote_token(self):
        """
        :return: quote token
        """
        return self.quote

    def get_base_token(self):
        """
        :return: base token
        """
        return self.base

    def get_symbol(self):
        """
        :return: symbol i.e. "SWTH_NEO"
        """
        return self.quote.get_name()+"_"+self.base.get_name()

    def load_tickers(self, start_time, end_time, interval):
        """
        Load candlesticks of requested interval
        :param start_time: start time
        :param end_time: end time
        :param interval: interval
        :return: list of candlesticks
        """
        params = {"start_time": start_time, "end_time": end_time, "interval": interval}
        raw_candles = request.public_request(self.exchange.get_url(), "/v2/tickers/candlesticks", params)
        self.candlesticks = []
        for entry in raw_candles:
            self.candlesticks.append(Candlestick(self, int(entry["time"]), float(entry["open"]),
                                     float(entry["close"]), float(entry["high"]), float(entry["low"]),
                                     float(entry["volume"]), float(entry["quote_volume"]), interval))
        return self.candlesticks

    def load_last_price(self):
        """
        Load last price of pairs
        :return: last price
        """
        self.last_price = float(request.public_request(self.exchange.get_url(), "/v2/tickers/last_price",
                                                       {self.get_quote_token().get_name()}))
        return self.last_price

    def set_last_price(self, price):
        """
        Set last price
        :param price: last price
        :return: None
        """
        self.last_price = price

    def get_last_price(self):
        """
        :return: last price
        """
        return self.last_price

    def load_offers(self, contract=None):
        """
        Load offers and create new order book.
        :param contract: contract
        :return: list of offers
        """
        if self.is_updating():
            return
        self.set_updating(True)
        if contract is None:
            contract = self.get_exchange().get_contract("NEO")
        params = {"blockchain": contract.get_blockchain().lower(), "pair": self.get_symbol(), "contract_hash": contract.get_latest_hash()}
        raw_offers = request.public_request(self.exchange.get_url(), "/v2/offers", params)
        self.offers = []
        for offer in raw_offers:
            way = Trade.WAY_BUY
            quote_amount = offer["want_amount"]
            base_amount = offer["offer_amount"]
            if offer["offer_asset"] == self.get_quote_token().get_name():
                way = Trade.WAY_SELL

                quote_amount = offer["offer_amount"]
                base_amount = offer["want_amount"]

            #if self.get_quote_token().get_decimals() == 0:
            #    quote_amount = quote_amount * pow(10, 8)

            price = base_amount / quote_amount



            if offer["available_amount"] < offer["offer_amount"]:
                quote_amount = int(offer["available_amount"] / offer["offer_amount"] * quote_amount)
                base_amount = int(offer["available_amount"] / offer["offer_amount"] * base_amount)

            self.offers.append(Offer(way, quote_amount, base_amount, price))
        self.orderbook = OrderBook(self, self.offers)
        log.log("pair.txt", "%s: updated" % self.get_symbol())
        self.fire_on_update()
        self.set_updating(False)
        return self.offers

    def get_orderbook(self):
        """
        :return: order book
        """
        return self.orderbook

    def get_exchange(self):
        """
        :return: get exchange
        """
        return self.exchange

    def is_updated(self):
        """
        Checks if pair is updated
        :return: true if updated
        """
        return self.orderbook is not None and self.orderbook.is_updated()

    def get_equal_token(self, tp):
        """
        Get the equal tokens of two pairs.
        :param tp: other pair
        :return: same token
        """
        if self.base == tp.get_base_token() or self.base == tp.get_quote_token():
            return self.base
        if self.quote == tp.get_quote_token() or self.quote == tp.get_base_token():
            return self.quote

    def add_on_update(self, callback):
        """
        Add a callback which is called after an update.
        :param callback:
        :return:
        """
        self.on_update_method.append(callback)

    def fire_on_update(self):
        """
        Calls all callbacks
        :return:
        """
        for callback in self.on_update_method:
            callback()

    def get_candlestick_24h(self):
        """
        :return: 24h candlestick
        """
        return self.candlestick_24h

    def set_candlestick_24h(self, candlestick):
        """
        Set 24h candlestick
        :param candlestick: 24h candlestick
        :return:
        """
        self.candlestick_24h = candlestick

    def __str__(self):
        """
        Pair to string
        :return: pair as string
        """
        return "Pair:%s Last Price:%.8f" % (self.get_symbol(), self.get_last_price())
