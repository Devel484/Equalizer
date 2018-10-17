"""
author: Devel484
"""


class Offer(object):

    def __init__(self, way, quote_amount, base_amount, price):
        """
        Sub object for OfferBook
        :param way: trade way
        :param quote_amount: quote amount
        :param base_amount: base amount
        :param price: price
        """
        self.way = way
        self.quote_amount = quote_amount
        self.base_amount = base_amount
        self.price = price
        self.sum_base = 0
        self.sum_quote = 0

    def get_way(self):
        """
        :return: trade way
        """
        return self.way

    def get_quote_amount(self):
        """
        :return: quote amount
        """
        return self.quote_amount

    def add_quote_amount(self, amount):
        """Add amount to quote
        :param amount: quote amount
        :return: None
        """
        self.quote_amount = self.quote_amount + amount

    def get_base_amount(self):
        """
        :return: base amount
        """
        return self.base_amount

    def add_base_amount(self, amount):
        """Add amount to base
        :param amount: base amount
        :return: None
        """
        self.base_amount = self.base_amount + amount

    def get_price(self):
        """
        :return: price
        """
        return self.price

    def get_sum_base(self):
        """Get sum of base of all offers before and self
        :return: sum amount base
        """
        return self.sum_base

    def set_sum_base(self, sum):
        """Set sum of base of all offers before and self
        :param sum: sum base amount
        :return: None
        """
        self.sum_base = sum

    def get_sum_quote(self):
        """Get sum of quote of all offers before and self
        :return: sum quote base
        """
        return self.sum_quote

    def set_sum_quote(self, sum):
        """Set sum of quote of all offers before and self
        :param sum: sum quote base
        :return:
        """
        self.sum_quote = sum
