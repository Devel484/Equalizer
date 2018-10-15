"""
author: Devel484
"""


class Candlestick(object):
    """
    Intervals as specified(Sep.27.18) at https://docs.switcheo.network/#tickers parameter interval.
    """
    INTERVAL_MIN_1 = 1
    INTERVAL_MIN_5 = 5
    INTERVAL_MIN_30 = 30
    """ 1 Hour """
    INTERVAL_MIN_60 = 60
    """ 6 Hours """
    INTERVAL_MIN_360 = 360
    """ 24 Hours """
    INTERVAL_MIN_1440 = 1440

    def __init__(self, pair, time, open, close, high, low, volume, quote_volume, interval):
        """
        Candlestick with following data:
        :param pair: reference to pair
        :param time: start timestamp in seconds
        :param open: open price
        :param close: close price
        :param high: high price
        :param low: low price
        :param volume: base volume
        :param quote_volume: quote volume
        :param interval: requested interval
        """
        self.pair = pair
        self.time = time
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.quote_volume = quote_volume
        self.interval = interval

    def get_pair(self):
        """
        :return: reference to pair
        """
        return self.pair

    def get_time(self):
        """
        :return: start timestamp in seconds
        """
        return self.time

    def get_open(self):
        """
        :return: open price
        """
        return self.open

    def get_close(self):
        """
        :return: close price
        """
        return self.close

    def get_high(self):
        """
        :return: high price
        """
        return self.high

    def get_low(self):
        """
        :return: low price
        """
        return self.low

    def get_volume(self):
        """
        :return: base volume
        """
        return self.volume

    def get_base_volume(self):
        """
        :return: base volume
        """
        return self.volume

    def get_quote_volume(self):
        """
        :return: quote volume
        """
        return self.quote_volume

    def get_interval(self):
        """
        :return: requested interval
        """
        return self.interval
