

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

        if way == Trade.WAY_BUY:
            self.fee_currency = self.pair.get_quote_token()
            self.fees = self.amount_quote * pair.get_exchange().get_fees()
            self.amount_quote = self.amount_quote - self.fees
        else:
            self.fee_currency = self.pair.get_base_token()
            self.fees = self.amount_base * pair.get_exchange().get_fees()
            self.amount_base = self.amount_base - self.fees

    def get_total(self):
        if self.way == Trade.WAY_BUY:
            return self.amount_quote + self.fees
        else:
            return self.amount_base + self.fees

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

    def get_amount_quote(self):
        return self.amount_quote

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
        return("%4s %8s %16.8f %4s for %16.8f %4s paying %16.8f %4s fees"% (self.get_trade_block(), self.pair.get_symbol(), self.amount_quote,
                                                                       self.pair.get_quote_token().get_name(), self.amount_base, self.pair.get_base_token().get_name(),
                                                                       self.fees, self.fee_currency.get_name()))

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
