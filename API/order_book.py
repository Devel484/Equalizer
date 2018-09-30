

class OrderBook(object):

    WAY_BUY = 0
    WAY_SELL = 1

    def __init__(self, pair, offers=None):
        self.book = {}
        self.book[OrderBook.WAY_BUY] = []
        self.book[OrderBook.WAY_SELL] = []
        self.pair = pair
        self.timestamp = 0

        if offers:
            for offer in offers:
                self.add(offer)

    def add(self, offer):

        self.book[offer.get_way()].append(offer)
        self.book[offer.get_way()] = sorted(self.book[offer.get_way()], key=lambda entry: entry.get_price(),
                                            reverse=(offer.get_way() == OrderBook.WAY_BUY))

    def reset(self):
        self.book = {}
        self.book[OrderBook.WAY_BUY] = []
        self.book[OrderBook.WAY_SELL] = []

    def print(self):
        print(self.timestamp)
        for i in range(len(self.book[OrderBook.WAY_SELL])-1,-1,-1):
            print("%.10f\t\t%.8f" % (self.book[OrderBook.WAY_SELL][i].get_price(),
                                     self.book[OrderBook.WAY_SELL][i].get_quote_amount()))
        print("-----------------------------------")
        for i in range(len(self.book[OrderBook.WAY_BUY])):
            print("%.10f\t\t%.8f" % (self.book[OrderBook.WAY_BUY][i].get_price(),
                                     self.book[OrderBook.WAY_BUY][i].get_quote_amount()))

    def sum_up(self):
        sum_base = 0
        sum_quote = 0
        for i in range(len(self.book[OrderBook.WAY_BUY])):
            offer = self.book[OrderBook.WAY_BUY][i]
            sum_base = sum_base + offer.get_base_amount()
            sum_quote = sum_quote + offer.get_quote_amount()
            offer.set_sum_base(sum_base)
            offer.set_sum_quote(sum_quote)

        sum_base = 0
        sum_quote = 0
        for i in range(len(self.book[OrderBook.WAY_SELL])):
            offer = self.book[OrderBook.WAY_SELL][i]
            sum_base = sum_base + offer.get_base_amount()
            sum_quote = sum_quote + offer.get_quote_amount()
            offer.set_sum_base(sum_base)
            offer.set_sum_quote(sum_quote)

    def taker(self, amount, token):

        if amount:
            self.amount = amount
        '''
        Pair:MAN-BTC
        Currency:BTC
        => Buy
        Price(i.e. 0.00003560): For each MAN is an amount BTC needed
        '''
        if self.pair.get_base_token() == token:
            print("Buy")
            #self.buy()

        '''
        Pair:MAN-BTC
        Currency:MAN
        => SELL
        Price(i.e. 0.00003560): For each MAN you get an amount BTC
        '''
        if self.pair.get_quote_token() == token:
            print("Sell")
            #self.sell()
