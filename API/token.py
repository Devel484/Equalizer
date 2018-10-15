

class Token(object):

    def __init__(self, name, decimals, hash):
        """
        Creates a token
        :param name: name of the token
        :param decimals: decimals of precision
        :param hash: hash of the token
        """
        self.name = name
        self.decimals = decimals
        self.hash = hash
        self.balance = 0
        self.volume = 0

    def get_name(self):
        """
        :return: name
        """
        return self.name

    def get_decimals(self):
        """
        :return: decimals
        """
        return self.decimals

    def get_hash(self):
        """
        :return: hash
        """
        return self.hash

    def set_balance(self, balance):
        """
        Set the balance of the token
        :param balance: balance
        :return: None
        """
        self.balance = balance

    def add_balance(self, balance):
        """
        Add balance to existing
        :param balance: balance
        :return: None
        """
        self.balance = self.balance + balance

    def get_balance(self):
        """
        :return: balance
        """
        return self.balance

    def set_volume(self, volume):
        """
        Set volume of the token
        :param volume: volume
        :return: None
        """
        self.volume = volume

    def add_volume(self, volume):
        """
        Add volume to existing
        :param volume: volume
        :return: None
        """
        self.volume = self.volume + volume

    def get_volume(self):
        """
        :return: volume
        """
        return self.volume

    def __str__(self):
        """
        Token to string
        :return: token as string
        """
        return "%s: Balance:%d Volume:%.3f" % (self.name, self.balance, self.volume)
