

class Offer(object):

    def __init__(self, way, quote_amount, base_amount, price):
        self.way = way
        self.quote_amount = quote_amount
        self.base_amount = base_amount
        self.price = price
        self.sum_base = 0
        self.sum_quote = 0

    def get_way(self):
        return self.way

    def get_quote_amount(self):
        return self.quote_amount

    def get_base_amount(self):
        return self.base_amount

    def get_price(self):
        return self.price

    def get_sum_base(self):
        return self.sum_base

    def set_sum_base(self, sum):
        self.sum_base = sum

    def get_sum_quote(self):
        return self.sum_quote

    def set_sum_quote(self, sum):
        self.sum_quote = sum
