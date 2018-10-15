"""
author: Devel484
"""
from API.trade import Trade
import time


class OrderBook(object):

    def __init__(self, pair, offers=None):
        """
        Create a sorted order book with offers
        :param pair: reference to pair
        :param offers: offers of the pair
        """
        self.book = {}
        self.book[Trade.WAY_BUY] = []
        self.book[Trade.WAY_SELL] = []
        self.pair = pair
        self.timestamp = time.time()

        if offers:
            for offer in offers:
                self.add(offer)
            self.sum_up()

    def get_timestamp(self):
        """
        :return: timestamp in seconds
        """
        return self.timestamp

    def set_timestamp(self, timestamp):
        """Set timestamp
        :param timestamp: timestamp in seconds
        :return: None
        """
        self.timestamp = timestamp

    def get(self, price, way):
        """Get offer at price in trading way. Offers with same price and way are combined to one.
        :param price: price
        :param way: trading way
        :return: offer
        """
        for offer in self.book[way]:
            if offer.get_price() == price:
                return offer
        return None

    def add(self, offer):
        """Add offer to offer book. If other offer with same price and way exists, add the amounts to the existing.
        Offers are correct sorted:
        SELL ASC
        BUY DESC
        :param offer: offer to add
        :return: None
        """
        other_offer = self.get(offer.get_price(), offer.get_way())
        if other_offer:
            other_offer.add_quote_amount(offer.get_quote_amount())
            other_offer.add_base_amount(offer.get_base_amount())
            return
        self.book[offer.get_way()].append(offer)
        self.book[offer.get_way()] = sorted(self.book[offer.get_way()], key=lambda entry: entry.get_price(),
                                            reverse=(offer.get_way() == Trade.WAY_BUY))

    def reset(self):
        """Reset the offer book
        :return:None
        """
        self.book = {}
        self.book[Trade.WAY_BUY] = []
        self.book[Trade.WAY_SELL] = []

    def __str__(self):
        """
        Offer book to string
        :return: offer book as string
        """
        string = ""
        for i in range(len(self.book[Trade.WAY_SELL])-1, -1, -1):
            string = string + "%.10f\t\t%.8f\n" % (self.book[Trade.WAY_SELL][i].get_price(),
                                                 self.book[Trade.WAY_SELL][i].get_quote_amount())
        string = string + "-----------------------------------\n"
        for i in range(len(self.book[Trade.WAY_BUY])):
            string = string +"%.10f\t\t%.8f\n" % (self.book[Trade.WAY_BUY][i].get_price(),
                                                self.book[Trade.WAY_BUY][i].get_quote_amount())
        return string

    def sum_up(self):
        """Sums each offer up
        :return: None
        """
        sum_base = 0
        sum_quote = 0
        for i in range(len(self.book[Trade.WAY_BUY])):
            offer = self.book[Trade.WAY_BUY][i]
            sum_base = sum_base + offer.get_base_amount()
            sum_quote = sum_quote + offer.get_quote_amount()
            offer.set_sum_base(sum_base)
            offer.set_sum_quote(sum_quote)

        sum_base = 0
        sum_quote = 0
        for i in range(len(self.book[Trade.WAY_SELL])):
            offer = self.book[Trade.WAY_SELL][i]
            sum_base = sum_base + offer.get_base_amount()
            sum_quote = sum_quote + offer.get_quote_amount()
            offer.set_sum_base(sum_base)
            offer.set_sum_quote(sum_quote)

    def taker(self, amount, token):
        """
        Simulates a taker trade with amount of token
        :param amount: offer amount
        :param token: offer token
        :return: get(want) amount
        """
        if self.pair.get_base_token() == token:
            return self.buy(amount)

        if self.pair.get_quote_token() == token:
            return self.sell(amount)

    def buy(self, amount):
        """
        Simulates taker buy trade
        :param amount: offer amount
        :return: trades, want amount
        """
        trades = []
        buy_amount = 0
        for i in range(len(self.book[Trade.WAY_SELL])):
            offer = self.book[Trade.WAY_SELL][i]
            amount_quote = offer.get_quote_amount()
            amount_base = offer.get_base_amount()
            price = offer.get_price()

            if amount_base >= amount:
                tmp = int("%d" % (amount / price))
                trade = Trade(self.pair, Trade.WAY_BUY, price, amount, tmp, None)
                buy_amount = buy_amount + trade.get_amount_quote()
                trades.append(trade)
                return trades, int(buy_amount)

            '''
            Is the offered amount less than needed, you can only buy the offered amount and continue with next offer.
            '''
            trade = Trade(self.pair, Trade.WAY_BUY, price, amount_base, amount_quote, None)
            buy_amount = buy_amount + trade.get_amount_quote()
            amount = amount - amount_base
            trades = trades + [trade]

        '''
        Not enough volume or amount to high
        '''
        raise KeyError("Not enough offers in orderbook. Low volume or amount to high.")

    def sell(self, amount):
        """
        Simulates taker sell trade
        :param amount: offer amount
        :return: get(want) amount, trades
        """
        trades = []
        sell_amount = 0
        for i in range(len(self.book[Trade.WAY_BUY])):
            offer = self.book[Trade.WAY_BUY][i]
            amount_quote = offer.get_quote_amount()
            amount_base = offer.get_base_amount()
            price = offer.get_price()

            if amount_quote >= amount:
                tmp = amount * price
                tmp = int(tmp)
                trade = Trade(self.pair, Trade.WAY_SELL, price, tmp, amount, None)
                sell_amount = sell_amount + trade.get_amount_base()
                trades.append(trade)
                return trades, int(sell_amount)

            '''
            Is the offered amount less than needed, you can only buy the offered amount and continue
            '''
            trade = Trade(self.pair, Trade.WAY_SELL, price, amount_base, amount_quote, None)
            amount = amount - amount_quote
            sell_amount = sell_amount + trade.get_amount_base()
            trades = trades + [trade]

        '''
        Not enough volume or amount to high
        '''
        raise KeyError("Not enough offers in orderbook. Low volume or amount to high.")

    def reverse_taker(self, amount, token):
        """
        Simulates reversed taker trade with means:
        How much do I need to offer to get amount of token after fees!
        :param amount: want amount after fees
        :param token: want token
        :return: offer amount before fees
        """
        if self.pair.get_base_token() == token:
            return self.reverse_buy(amount)

        if self.pair.get_quote_token() == token:
            return self.reverse_sell(amount)

    def reverse_buy(self, amount):
        """
        Simulates reversed taker buy trade
        :param amount: want amount after fees
        :return: offer amount before fees
        """
        trade_amount = 0
        for i in range(len(self.book[Trade.WAY_SELL])):
            offer = self.book[Trade.WAY_SELL][i]
            amount_quote = offer.get_quote_amount() # GAS
            amount_base = offer.get_base_amount() # NEO
            price = offer.get_price()

            if amount_quote >= amount:
                trade_amount = trade_amount + amount*price / (1 - self.pair.get_exchange().get_fees())
                return int(trade_amount)

            '''
            Is the offered amount less than needed, you can only buy the offered amount and continue
            '''
            trade_amount = trade_amount + amount_base
            amount = amount - amount_quote

        '''
        Not enough volume or amount to high
        '''
        raise KeyError("Not enough offers in orderbook. Low volume or amount to high.")

    def reverse_sell(self, amount):
        """
        Simulates reversed taker sell trade
        :param amount: want amount after fees
        :return: offer amount before fees
        """
        trade_amount = 0
        for i in range(len(self.book[Trade.WAY_BUY])):
            offer = self.book[Trade.WAY_BUY][i]
            amount_quote = offer.get_quote_amount() # GAS
            amount_base = offer.get_base_amount() # NEO
            price = offer.get_price()

            if amount_base >= amount:
                trade_amount = trade_amount + amount/price / (1 - self.pair.get_exchange().get_fees())
                return int(trade_amount)

            '''
            Is the offered amount less than needed, you can only buy the offered amount and continue
            '''
            trade_amount = trade_amount + amount_quote
            amount = amount - amount_base

        '''
        Not enough volume or amount to high
        '''
        raise KeyError("Not enough offers in orderbook. Low volume or amount to high.")

    def is_updated(self):
        """
        Checks if offer book is updated
        :return: true if updated
        """
        return self.timestamp > 0

    def get_taker_trade_way(self, token):
        """
        Returns the trade way of taker buy offering token
        :param token: offer token
        :return: trade way
        """
        if self.pair.get_base_token() == token:
            return Trade.WAY_BUY

        if self.pair.get_quote_token() == token:
            return Trade.WAY_SELL

    def get_maker_trade_way(self, token):
        """
        Returns the trade way of maker buy offering token
        :param token: offer token
        :return: trade way
        """
        if self.pair.get_base_token() == token:
            return Trade.WAY_SELL

        if self.pair.get_quote_token() == token:
            return Trade.WAY_BUY

    def get_sum(self, index, way, token):
        """
        Return the sum of all offers til index in trade way of token.
        :param index: sum til index
        :param way: trade way
        :param token: requested sum of token(quote/base)
        :return: sum
        """
        if len(self.book[way]) <= index:
            return None

        if token == self.pair.get_quote_token():
            return self.book[way][index].get_sum_quote()
        else:
            return self.book[way][index].get_sum_base()

    def get_sum_after_fees(self, index, way, token):
        """
        Return the sum after fees of all offers til index in trade way of token.
        :param index: sum til index
        :param way: trade way
        :param token: requested sum of token(quote/base)
        :return: sum after fees
        """
        sum = self.get_sum(index, way, token)
        if not sum:
            return None
        return int(sum * (1-self.pair.get_exchange().get_fees()))

