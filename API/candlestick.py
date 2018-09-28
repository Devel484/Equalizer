

class Candlestick(object):
    """
    Intervals as specified(Sep.27.18) at https://docs.switcheo.network/#tickers parameter interval.
    """
    INTERVAL_MIN_1 = 1
    INTERVAL_MIN_5 = 5
    INTERVAL_MIN_30 = 30
    INTERVAL_MIN_60 = 60
    INTERVAL_MIN_360 = 360
    INTERVAL_MIN_1440 = 1440

    def __init__(self, pair, time, open, close, high, low, volume, quote_volume, interval):
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
        return self.pair

    def get_time(self):
        return self.time

    def get_open(self):
        return self.open

    def get_close(self):
        return self.close

    def get_high(self):
        return self.high

    def get_low(self):
        return self.low

    def get_volume(self):
        return self.volume

    def get_base_volume(self):
        return self.volume

    def get_quote_volume(self):
        return self.quote_volume

    def get_interval(self):
        return self.interval
