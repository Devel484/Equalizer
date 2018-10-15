

class Trade(object):
    TRADE_TYPE_MARKET = 0
    TRADE_TYPE_LIMIT = 1

    STATE_VIRTUAL = 0
    STATE_PENDING = 1
    STATE_PART_FILLED = 2
    STATE_FILLED = 3
    STATE_CANCELED = 4
    STATE_ACTIVE = 5

    WAY_BUY = 0
    WAY_SELL = 1

    def __init__(self, pair, way, price, amount_base, amount_quote, timestamp, type=TRADE_TYPE_LIMIT, state=STATE_VIRTUAL):
        """
        Create a Trade
        :param pair: pair reference
        :param way: trading way
        :param price: price
        :param amount_base: amount base
        :param amount_quote: amount quote
        :param timestamp: timestamp in seconds
        :param type: type of trade
        :param state: state of strade
        """
        self.pair = pair
        self.way = way
        self.type = type
        self.price = price
        self.amount_base = amount_base
        self.amount_quote = amount_quote
        self.filled = 0

        self.timestamp = timestamp
        self.state = state
        self.total = 0

        if way == Trade.WAY_BUY:
            self.total = self.amount_quote
            self.fee_currency = self.pair.get_quote_token()
            self.fees = int(self.amount_quote * pair.get_exchange().get_fees())
            self.amount_quote = self.amount_quote - self.fees
        else:
            self.total = self.amount_base
            self.fee_currency = self.pair.get_base_token()
            self.fees = int(self.amount_base * pair.get_exchange().get_fees())
            self.amount_base = self.amount_base - self.fees

    def get_total(self):
        """
        :return: amount before fees
        """
        return self.total

    def get_offer(self):
        """
        :return: offer amount
        """
        if self.way == Trade.WAY_BUY:
            return self.amount_base
        else:
            return self.amount_quote

    def get_want(self):
        """
        :return: want amount
        """
        if self.way == Trade.WAY_BUY:
            return self.amount_quote + self.fees
        else:
            return self.amount_base + self.fees

    def get_pair(self):
        """
        :return: pair
        """
        return self.pair

    def get_way(self):
        """
        :return: way
        """
        return self.way

    def get_type(self):
        """
        :return: type
        """
        return self.type

    def get_price(self):
        """
        :return: price
        """
        return self.price

    def get_amount_base(self):
        """
        :return: amount base
        """
        return self.amount_base

    def get_amount_base_as_float(self):
        """
        :return: amount base as float
        """
        return self.amount_base / pow(10, self.pair.get_base_token().get_decimals())

    def get_amount_quote(self):
        """
        :return: amount quote
        """
        return self.amount_quote

    def get_amount_quote_as_float(self):
        """
        :return: amount quote as float
        """
        return self.amount_quote / pow(10, self.pair.get_quote_token().get_decimals())

    def is_filled(self):
        """
        :return: true if filled
        """
        return self.state == Trade.STATE_FILLED

    def is_part_filled(self):
        """
        :return: true if partial filled
        """
        return self.state == Trade.STATE_PART_FILLED

    def is_pending(self):
        """
        :return: true if pending
        """
        return self.state == Trade.STATE_PENDING

    def is_active(self):
        """
        :return: true if active
        """
        return self.state == Trade.STATE_ACTIVE

    def is_canceled(self):
        """
        :return: true if canceled
        """
        return self.state == Trade.STATE_CANCELED

    def is_virtual(self):
        """
        :return: true if virtual
        """
        return self.state == Trade.STATE_VIRTUAL

    def set_state(self, state):
        """
        :param state: state
        :return: None
        """
        self.state = state

    def get_timestamp(self):
        """
        :return: timestamp in seconds
        """
        return self.timestamp

    def get_fees(self):
        """
        :return: fee amount
        """
        return self.fees

    def get_fees_as_float(self):
        """
        :return: fees as float
        """
        return self.fees / pow(10, self.fee_currency.get_decimals())

    def is_market(self):
        """
        :return: true if market trade
        """
        return self.type == Trade.TRADE_TYPE_MARKET

    def is_limit(self):
        """
        :return: true if taker trade
        """
        return self.type == Trade.TRADE_TYPE_LIMIT

    def __str__(self):
        """
        Trade to string
        :return: trade as string
        """
        return("[%9s] %4s %16.8f %4s @ %.8f for %16.8f %4s paying %16.8f %4s fees" %
               (self.pair.get_symbol(), self.get_trade_way_as_string(),
                self.get_amount_quote_as_float(),
                self.pair.get_quote_token().get_name(),
                self.price,
                self.get_amount_base_as_float(),
                self.pair.get_base_token().get_name(),
                self.get_fees_as_float(),
                self.fee_currency.get_name()))

    def get_trade_way_as_string(self):
        """
        :return: trade way as string
        """
        if self.way == Trade.WAY_BUY:
            return Trade.get_buy_string()
        return Trade.get_sell_string()

    def create_order(self):
        exchange = self.pair.get_exchange()

    @staticmethod
    def get_buy_string():
        """
        :return: "BUY"
        """
        return "BUY"

    @staticmethod
    def get_sell_string():
        """
        :return: "SELL"
        """
        return "SELL"

    @staticmethod
    def combine(trades):
        """
        Combine a trades to one new trade
        :param trades: list of trades
        :return: trade
        """
        if len(trades) == 0:
            return None
        amount_quote = 0
        amount_base = 0
        pair = trades[0].get_pair()
        way = trades[0].get_way()
        price = trades[0].get_price()
        timestamp = trades[0].get_timestamp()
        for trade in trades:
            if trade.get_way() != way:
                raise TypeError("Trading ways are different")
            if trade.get_pair() != pair:
                raise TypeError("Trading pairs are different")
            if trade.get_way() == Trade.WAY_BUY:
                amount_quote = amount_quote + trade.get_total()
                amount_base = amount_base + trade.get_amount_base()
            else:
                amount_quote = amount_quote + trade.get_amount_quote()
                amount_base = amount_base + trade.get_total()
            price = trade.get_price()
        if amount_quote == 0 or amount_base == 0:
            raise ValueError("Amount is Zero")
        return Trade(pair, way, price, amount_base, amount_quote, timestamp)
