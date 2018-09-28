

class Token(object):

    def __init__(self, name, decimals, hash):
        self.name = name
        self.decimals = decimals
        self.hash = hash

    def get_name(self):
        return self.name

    def get_decimals(self):
        return self.decimals

    def get_hash(self):
        return self.hash
