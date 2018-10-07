

class Token(object):

    def __init__(self, name, decimals, hash):
        self.name = name
        self.decimals = decimals
        self.hash = hash
        self.balance = 0
        self.volume = 0

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

    def set_volume(self, volume):
        self.volume = volume

    def add_volume(self, volume):
        self.volume = self.volume + volume

    def get_volume(self):
        return self.volume


    def __str__(self):
        return "%s: Balance:%d Volume:%.3f" % (self.name, self.balance, self.volume)
