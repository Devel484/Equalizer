

class Token(object):

    def __init__(self, name, decimals, hash):
        self.name = name
        self.decimals = decimals
        self.hash = hash
        self.balance = 0

    def get_name(self):
        return self.name

    def get_decimals(self):
        return self.decimals

    def get_hash(self):
        return self.hash

    def set_balance(self, balance):
        self.balance = balance

    def get_balance(self):
        return self.balance

    def __str__(self):
        return "%s: %f" % (self.name, self.balance)
