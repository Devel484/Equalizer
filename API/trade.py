

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
        return self.total

    def get_offer(self):
        if self.way == Trade.WAY_SELL:
            return self.amount_base
        else:
            return self.amount_quote

    def get_want(self):
        if self.way == Trade.WAY_SELL:
            return int(self.amount_quote + self.fees)
        else:
            return int(self.amount_base + self.fees)


    def get_pair(self):
        return self.pair

    def get_way(self):
        return self.way

    def get_type(self):
        return self.type

    def get_price(self):
        return self.price

    def get_amount_base(self):
        return self.amount_base

    def get_amount_base_as_float(self):
        return self.amount_base / pow(10, self.pair.get_base_token().get_decimals())

    def get_amount_quote(self):
        return self.amount_quote

    def get_amount_quote_as_float(self):
        return self.amount_quote / pow(10, self.pair.get_quote_token().get_decimals())

    def is_filled(self):
        return self.state == Trade.STATE_FILLED

    def is_part_filled(self):
        return self.state == Trade.STATE_PART_FILLED

    def is_pending(self):
        return self.state == Trade.STATE_PENDING

    def is_active(self):
        return self.state == Trade.STATE_ACTIVE

    def is_cancaled(self):
        return self.state == Trade.STATE_CANCELED

    def is_virtual(self):
        return self.state == Trade.STATE_VIRTUAL

    def set_state(self, state):
        self.state = state

    def get_timestamp(self):
        return self.timestamp

    def get_fees(self):
        return self.fees

    def is_market(self):
        return self.type == Trade.TRADE_TYPE_MARKET

    def is_limit(self):
        return self.type == Trade.TRADE_TYPE_LIMIT

    def __str__(self):
        return("%4s %8s %16.8f %4s for %16.8f %4s paying %16.8f %4s fees @ %.8f" %
               (self.get_trade_block(), self.pair.get_symbol(),
                (self.amount_quote/pow(10, self.pair.get_quote_token().get_decimals())),
                self.pair.get_quote_token().get_name(),
                (self.amount_base/pow(10, self.pair.get_base_token().get_decimals())),
                self.pair.get_base_token().get_name(),
                (self.fees/pow(10, self.fee_currency.get_decimals())),
                self.fee_currency.get_name(),
                self.price))

    def get_trade_block(self):
        if self.way == Trade.WAY_BUY:
            return self.get_green_block()
        return self.get_red_block()

    def get_green_block(self):
        #return '\033[92m'+"#"+'\033[0m'
        return "BUY"

    def get_red_block(self):
        #return '\033[91m'+"#"+'\033[0m'
        return "SELL"

    @staticmethod
    def combine(trades):
        if len(trades)==0:
            return None
        amount_quote = 0
        amount_base = 0
        pair = trades[0].get_pair()
        way = trades[0].get_way()
        timestamp = trades[0].get_timestamp()
        for trade in trades:
            if trade.get_way() != way:
                raise TypeError("Trading ways are different")
            if trade.get_pair() != pair:
                raise TypeError("Trading pairs are different")
            if trade.get_way() == Trade.WAY_BUY:
                amount_quote = trade.get_total()
                amount_base = trade.get_amount_base()
            else:
                amount_quote = trade.get_amount_quote()
                amount_base = trade.get_total()
        if amount_quote == 0 or amount_base == 0:
            return None
        return Trade(pair, way, amount_base/amount_quote, amount_base, amount_quote, timestamp)
