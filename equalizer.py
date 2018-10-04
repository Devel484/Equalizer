from API.pair import Pair
import API.log
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
        self.execute(calc[3])
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
                start_market = self.start_pair.get_orderbook()
                middle_market = self.middle_pair.get_orderbook()
                end_market = self.end_pair.get_orderbook()
                max_possible_start = start_market.get_sum_after_fees(i, start_market.get_maker_trade_way(self.outter_currency), self.inner_first_currency)
                max_possible_middle = middle_market.get_sum(i, middle_market.get_maker_trade_way(self.inner_first_currency), self.inner_first_currency)

                if max_possible_start > max_possible_middle:
                    max_possible_start = max_possible_middle

                max_possible_middle = middle_market.get_sum_after_fees(i, middle_market.get_maker_trade_way(self.inner_first_currency), self.inner_second_currency)
                max_possible_end = end_market.get_sum(i, end_market.get_maker_trade_way(self.inner_second_currency), self.inner_second_currency)

                if max_possible_middle > max_possible_end:
                    max_possible_middle = max_possible_end
                    tmp = self.middle_pair.get_orderbook().reverse_taker(max_possible_middle, self.inner_first_currency)
                    if tmp < max_possible_start:
                        max_possible_start = tmp

                start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outter_currency)
                end_with, trades = self.calc(start_with)

                win = end_with-start_with

                if len(trades) > 3 and i==0:
                    continue


                API.log.log("equalizer_win.txt", "%s:%.8f (%.2f%%)" % (self.get_symbol(), win, win/start_with * 100))
                for trade in trades:
                    API.log.log("equalizer_win.txt", "%s" % trade)

                if win > 0:
                    for trade in trades:
                        pair = trade.get_pair()
                        exchange = pair.get_exchange()
                        print(trade)
                        if exchange.get_minimum_amount(pair.get_base_token()) > trade.get_amount_base():
                            print("Not enougth")
                            return
                        if exchange.get_minimum_amount(pair.get_quote_token()) > trade.get_amount_quote():
                            print("Not enougth")
                            return
                    best_win.append((win, start_with, end_with, trades))
                else:
                    break
                i = i + 1
            except Exception as e:
                print(e)
                break

        if len(best_win) > 0:
            best_win = sorted(best_win, key=lambda entry: entry[0], reverse=True)
            self.calc(best_win[0][1])
            self.printWin(best_win[0])


        #print(max_possible_middle)
        #print(max_possible_end)

    def get_symbol(self):
        return self.ticker

    def execute(self, trades):
        for trade in trades:

            print(trade.get_pair().get_exchange().client.create_order(trade.get_pair().get_exchange().kp, trade.get_pair().get_symbol(),
                                                                     trade.get_trade_block().lower(), trade.get_price(),
                                                                     trade.get_total()))
