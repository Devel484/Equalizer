from API.pair import Pair

import time

class Equalizer():

    def __init__(self, start_pair, middle_pair, end_pair):
        # MAN-BTC -> MAN-ETH -> ETH-BTC
        # BTC-MAN-ETH-BTC
        self.outter_currency = start_pair.get_equal_token(end_pair)
        self.inner_first_currency = start_pair.get_equal_token(middle_pair)
        self.inner_second_currency = middle_pair.get_equal_token(end_pair)

        if self.outter_currency is None or \
                self.inner_first_currency is None or \
                self.inner_second_currency is None:
            print("[Equalizer] %s %s %s not possible" % (start_pair.get_symbol(),
                                                         middle_pair.get_symbol(),
                                                         end_pair.get_symbol()))
            return
        self.ticker = "%s-%s-%s-%s" %(self.outter_currency.get_name(),
                                      self.inner_first_currency.get_name(),
                                      self.inner_second_currency.get_name(),
                                      self.outter_currency.get_name())

        self.start_pair = start_pair
        start_pair.add_on_update(self.update)
        self.middle_pair = middle_pair
        middle_pair.add_on_update(self.update)
        self.end_pair = end_pair
        end_pair.add_on_update(self.update)

        self.start_market = start_pair.get_orderbook()
        self.middle_market = middle_pair.get_orderbook()
        self.end_market = end_pair.get_orderbook()

        self.total_win = 0
        self.last = 0
        self.timestamp = 0

    def update(self):
        if not self.start_pair.is_updated():
            return

        if not self.middle_pair.is_updated():
            return

        if not self.end_pair.is_updated():
            return

        if self.start_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.start_pair.get_orderbook().get_timestamp()

        if self.middle_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.middle_pair.get_orderbook().get_timestamp()

        if self.end_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.end_pair.get_orderbook().get_timestamp()

        self.get_best_amount()

        '''self.calc()

        end_amount = self.end_market.getTotal()
        win = end_amount-self.amount
        if end_amount > self.amount and not win == self.last:
            self.total_win = self.total_win + win

            #self.print()

            self.getBestAmount()

            #self.start_market.print()
            #self.middle_market.print()
            #self.end_market.print()





        self.last = win'''

    def printWin(self, amount=None):

        if not amount:
            amount = self.amount
        end_amount = self.end_market.getTotal()
        win = end_amount-amount
        #if end_amount > self.amount and not win == self.last:
        ftime = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(self.timestamp))

        print("[%s][%s]%s Win:%16.8f Total:%16.8f" %(ftime, self.start_tradingPair.getExchange().getName(), \
                                                     self.ticker,  win, self.total_win))

        self.start_market.print()
        self.middle_market.print()
        self.end_market.print()
        self.print()
        return

    def calc(self, amount):
        self.start_market.trade(amount)
        self.middle_market.trade(self.start_market.getTotal())
        self.end_market.trade(self.middle_market.getTotal())


    def get_best_amount(self):

        best_win = []
        i = 0
        while True:
            max_possible_start = self.start_pair.get_orderbook().get_sum_after_fees(i, self.inner_first_currency)
            max_possible_middle = self.middle_pair.get_orderbook().get_sum(i, self.inner_first_currency)

            if max_possible_start > max_possible_middle:
                max_possible_start = max_possible_middle

            print(max_possible_start)
            print(max_possible_middle)

            max_possible_middle = self.middle_pair.get_orderbook().get_sum_after_fees(i, self.inner_second_currency)
            max_possible_end = self.end_pair.get_orderbook().get_sum(i, self.inner_second_currency)

            if max_possible_middle > max_possible_end:
                max_possible_middle = max_possible_end
                max_possible_start = self.middle_pair.get_orderbook().reverse_taker(max_possible_middle, self.inner_first_currency)

            start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outter_currency)
            self.calc(start_with)

            end_with = self.end_pair.get_orderbook.getTotal()
            win = end_with-start_with
            if win > 0.00000100:
                best_win.append((win, start_with))
            else:
                break
            i = i + 1

        if len(best_win) > 0:
            best_win = sorted(best_win, key=self.getKey, reverse=True)
            self.amount = best_win[0][1]
            self.calc(best_win[0][1])
            self.printWin()


        #print(max_possible_middle)
        #print(max_possible_end)

    def getKey(self, item):
        return item[0]

    def print(self):


        max_entries = 5

        if len(self.start_market.getTrades()) > max_entries:
            max_entries = len(self.start_market.getTrades())

        if len(self.middle_market.getTrades()) > max_entries:
            max_entries = len(self.middle_market.getTrades())

        if len(self.end_market.getTrades()) > max_entries:
            max_entries = len(self.end_market.getTrades())

        for i in range(max_entries-1, -1 , -1):
            print(self.getPrintString(OrderBook.WAY_SELL, i))

        for i in range(max_entries):
            print(self.getPrintString(OrderBook.WAY_BUY, i))

    def getPrintString(self, way, index):
        s_book = self.start_tradingPair.getOrderBook().book
        m_book = self.middle_tradingPair.getOrderBook().book
        e_book = self.end_tradingPair.getOrderBook().book
        string = ""
        if not self.start_market.getTradeWay() == way:
            string = "%s %.10f %20.8f " % (string, \
                                           s_book[way][index][OrderBook.INDEX_PRICE], \
                                           s_book[way][index][OrderBook.INDEX_AMOUNT])
        else:
            string = "%s %11s %21s" % (string, "", "")

        if not self.middle_market.getTradeWay() == way:
            string = "%s %.10f %20.8f " % (string, \
                                           m_book[way][index][OrderBook.INDEX_PRICE], \
                                           m_book[way][index][OrderBook.INDEX_AMOUNT])
        else:
            string = "%s %11s %21s" % (string, "", "")

        if not self.end_market.getTradeWay() == way:
            string = "%s %.10f %20.8f " % (string, \
                                           e_book[way][index][OrderBook.INDEX_PRICE], \
                                           e_book[way][index][OrderBook.INDEX_AMOUNT])
        else:
            string = "%s %11s %21s" % (string, "", "")

        return string



