

class Offer(object):

    def __init__(self, way, quote_amount, base_amount, price):
        self.way = way
        self.quote_amount = quote_amount
        self.base_amount = base_amount
        self.price = price

    def get_way(self):
        return self.way

    def get_quote_amount(self):
        return self.quote_amount

    def get_base_amount(self):
        return self.base_amount

    def get_price(self):
        return self.price
