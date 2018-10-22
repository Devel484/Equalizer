

class Trade(object):
    TRADE_TYPE_TAKER = 0
    TRADE_TYPE_MAKER = 1

    STATE_VIRTUAL = 0
    STATE_PENDING = 1
    STATE_PART_FILLED = 2
    STATE_FILLED = 3
    STATE_CANCELED = 4
    STATE_ACTIVE = 5

    WAY_BUY = 0
    WAY_SELL = 1

    def __init__(self, pair, way, price, amount_base, amount_quote, timestamp, type=TRADE_TYPE_TAKER, state=STATE_VIRTUAL, id=None, filled=1, fee_currency=None, fees=None):
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
        self.filled = filled

        self.timestamp = timestamp
        self.state = state
        self.total = 0

        self.id = id

        if way == Trade.WAY_BUY:
            self.total = self.amount_quote
            if fee_currency:
                self.fee_currency = fee_currency
                self.fees = fees
            else:
                self.fee_currency = self.pair.get_quote_token()
                self.pair.get_exchange().calculate_fees(self)
                self.amount_quote = self.amount_quote - self.fees
        else:
            self.total = self.amount_base
            if fee_currency:
                self.fee_currency = fee_currency
                self.fees = fees
            else:
                self.fee_currency = self.pair.get_base_token()
                self.pair.get_exchange().calculate_fees(self)
                self.amount_base = self.amount_base - self.fees

        if self.fees is None:
            self.pair.get_exchange().calculate_fees(self)

    def get_id(self):
        """
        Get identification
        :return: id
        """
        return self.id

    def set_id(self, id):
        """
        Set identification
        :param id: id
        :return: None
        """
        self.id = id

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
            if self.pair.get_quote_token() == self.fee_currency and self.pair.get_quote_token().get_name() != "SWTH":
                return self.amount_quote + self.fees
            return self.amount_quote
        else:
            if self.pair.get_base_token() == self.fee_currency and self.pair.get_base_token().get_name() != "SWTH":
                return self.amount_base + self.fees
            return self.amount_base

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

    def get_filled(self):
        """
        Get filled in percentage
        :return: %
        """
        return self.filled

    def set_filled(self, filled):
        """
        Set filled(%)
        :param filled: filled in percentage
        :return: None
        """
        self.filled = filled

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

    def get_fee_token(self):
        """
        Get the token in which the fees are paid
        :return: Token
        """
        return self.fee_currency

    def set_fees(self, fees):
        """
        Set the fees
        :param fees: fees
        :return: None
        """
        self.fees = fees

    def get_fees(self):
        """
        :return: fee amount
        """
        return self.fees

    def get_fees_as_float(self):
        """
        :return: fees as float
        """
        decimals = self.fee_currency.get_decimals()
        if decimals == 0:
            decimals = 8
        return self.fees / pow(10, decimals)

    def is_maker(self):
        """
        :return: true if maker trade
        """
        return self.type == Trade.TRADE_TYPE_MAKER

    def is_taker(self):
        """
        :return: true if taker trade
        """
        return self.type == Trade.TRADE_TYPE_TAKER

    def get_state_as_string(self):
        """
        Get state as string
        (V)irtual
        (P)ending
        (A)ctive
        (F)illed
        (f)illed part.
        (X)Canceled
        (?)Unknown
        :return: state as string
        """
        if self.is_virtual():
            return "V"
        if self.is_pending():
            return "P"

        if self.is_active():
            return "A"

        if self.is_filled():
            return "F"

        if self.is_part_filled():
            return "f"

        if self.is_canceled():
            return "X"

        return "?"

    def get_type_as_string(self):
        """
        Get the type as string:
        (M)aker
        (T)aker
        (?)Unknown
        :return: type as string
        """
        if self.is_taker():
            return "T"

        if self.is_maker():
            return "M"

        return "?"

    def __str__(self):
        """
        Trade to string
        :return: trade as string
        """

        return("[%9s][%s][%s][%3d%%] %4s %16.8f %4s @ %.8f for %16.8f %4s paying %16.8f %4s fees" %
               (self.pair.get_symbol(),
                self.get_type_as_string(),
                self.get_state_as_string(),
                self.get_filled()*100,
                self.get_trade_way_as_string(),
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

    def send_order(self):
        exchange = self.pair.get_exchange()
        return exchange.send_order(self)

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
        fee_currency = trades[0].get_fee_token()
        for trade in trades:
            if trade.get_way() != way:
                raise TypeError("Trading ways are different")
            if trade.get_pair() != pair:
                raise TypeError("Trading pairs are different")
            if trade.get_fee_token() != fee_currency:
                raise TypeError("Fee token is not correct")

            """if len(trades) > 1 and trade == trades[len(trades)-1]:
                exchange = pair.get_exchange()
                if exchange.get_minimum_amount(pair.get_quote_token()) > trade.get_amount_quote():
                    raise ValueError("Last amount to small")

                if exchange.get_minimum_amount(pair.get_base_token()) > trade.get_amount_base():
                    raise ValueError("Last amount to small")"""

            if trade.get_way() == Trade.WAY_BUY:
                amount_quote = amount_quote + trade.get_total()
                amount_base = amount_base + trade.get_amount_base()
            else:
                amount_quote = amount_quote + trade.get_amount_quote()
                amount_base = amount_base + trade.get_total()
            price = trade.get_price()
        if amount_quote == 0 or amount_base == 0:
            raise ValueError("[%s]Amount is Zero" % pair.get_symbol())
        return Trade(pair, way, price, amount_base, amount_quote, timestamp, fee_currency=fee_currency)

    @staticmethod
    def get_trade_way(way_string):
        """
        Get trade way by string
        :param way_string: "sell" or "buy"
        :return: as integer
        """
        if way_string.lower() == "buy":
            return Trade.WAY_BUY
        if way_string.lower() == "sell":
            return Trade.WAY_SELL
        raise ValueError("Trade way string not possible:"+way_string)
