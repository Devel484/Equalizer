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
                self.inner_second_currency is None or \
                start_pair == middle_pair or \
                middle_pair == end_pair or \
                start_pair == end_pair or \
                self.outter_currency == self.inner_first_currency or \
                self.inner_first_currency == self.inner_second_currency or\
                self.inner_second_currency == self.outter_currency:
            raise ValueError("[Equalizer] %s %s %s not possible" % (start_pair.get_symbol(),
                                                                    middle_pair.get_symbol(),
                                                                    end_pair.get_symbol()))
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

    def printWin(self, calc):
        win =calc[0]
        amount = calc[1]
        end_amount = calc[2]
        #if end_amount > self.amount and not win == self.last:
        ftime = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(self.timestamp))
        percentage = win/amount * 100
        print("[%s]%s use %16.8f %s to make %16.8f %s (%.3f%%)" %(ftime, self.ticker, amount, self.outter_currency.get_name(),
                                                         win, self.outter_currency.get_name(), percentage))

        for trade in calc[3]:
            print(trade)
        #self.start_market.print()
        #self.middle_market.print()
        #self.end_market.print()
        #self.print()
        return

    def calc(self, amount):
        try:
            all_trades, amount = self.start_pair.get_orderbook().taker(amount, self.outter_currency)
            trades, amount = self.middle_pair.get_orderbook().taker(amount, self.inner_first_currency)
            all_trades = all_trades + trades
            trades, amount = self.end_pair.get_orderbook().taker(amount, self.inner_second_currency)
            all_trades = all_trades + trades
            return amount, all_trades
        except KeyError:
            return 0, []



    def get_best_amount(self):

        best_win = []
        i = 0
        while True:
            try:
                max_possible_start = self.start_pair.get_orderbook().get_sum_after_fees(i, self.inner_first_currency)
                max_possible_middle = self.middle_pair.get_orderbook().get_sum(i, self.inner_first_currency)

                if max_possible_start > max_possible_middle:
                    max_possible_start = max_possible_middle

                max_possible_middle = self.middle_pair.get_orderbook().get_sum_after_fees(i, self.inner_second_currency)
                max_possible_end = self.end_pair.get_orderbook().get_sum(i, self.inner_second_currency)

                if max_possible_middle > max_possible_end:
                    max_possible_middle = max_possible_end
                    max_possible_start = self.middle_pair.get_orderbook().reverse_taker(max_possible_middle, self.inner_first_currency)

                start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outter_currency)
                end_with, trades = self.calc(start_with)

                win = end_with-start_with
                #print(win)
                if win > 0:
                    best_win.append((win, start_with, end_with, trades))
                else:
                    break
                i = i + 1
            except Exception:
                break

        if len(best_win) > 0:
            best_win = sorted(best_win, key=lambda entry: entry[0], reverse=True)
            self.amount = best_win[0][1]
            self.calc(best_win[0][1])
            self.printWin(best_win[0])


        #print(max_possible_middle)
        #print(max_possible_end)

    def get_symbol(self):
        return self.ticker
