import API.log
import time
from API.trade import Trade


class Equalizer(object):

    def __init__(self, start_pair, middle_pair, end_pair, start_with=None):
        """
        Create Arbitrage markets
        :param start_pair: start with pair
        :param middle_pair: trade over pair
        :param end_pair: end with pair
        :param start_with: start with token
        """
        self.outer_currency = start_pair.get_equal_token(end_pair)
        self.inner_first_currency = start_pair.get_equal_token(middle_pair)
        self.inner_second_currency = middle_pair.get_equal_token(end_pair)
        if self.outer_currency is None or \
                self.inner_first_currency is None or \
                self.inner_second_currency is None or \
                start_pair == middle_pair or \
                middle_pair == end_pair or \
                start_pair == end_pair or \
                (start_with is not None and start_with != self.outer_currency) or \
                self.outer_currency == self.inner_first_currency or \
                self.inner_first_currency == self.inner_second_currency or\
                self.inner_second_currency == self.outer_currency:
            raise ValueError("[Equalizer] %s %s %s not possible" % (start_pair.get_symbol(),
                                                                    middle_pair.get_symbol(),
                                                                    end_pair.get_symbol()))
        self.ticker = "%s-%s-%s-%s" %(self.outer_currency.get_name(),
                                      self.inner_first_currency.get_name(),
                                      self.inner_second_currency.get_name(),
                                      self.outer_currency.get_name())

        self.start_pair = start_pair
        self.middle_pair = middle_pair
        self.end_pair = end_pair

        self.start_market = start_pair.get_orderbook()
        self.middle_market = middle_pair.get_orderbook()
        self.end_market = end_pair.get_orderbook()

        self.timestamp = 0
        self.spread = 0
        self.updating = False
        self.view_only = True

    def toggle_view_only(self, b):
        """
        Toggle view only. If set it only prints and do not check and execute.
        :param b: bool
        :return: None
        """
        self.view_only = b

    def get_start_token(self):
        """
        :return: start token
        """
        return self.outer_currency

    def is_updating(self):
        """
        :return: true while loading order books
        """
        return self.updating

    def set_updating(self, b):
        """
        Set updating
        :param b: state
        :return: None
        """
        self.updating = b

    def update(self):
        """
        Update all markets and recalculate profits
        :return: None
        """
        if self.is_updating():
            return
        API.log.log("update.txt", "%s:%s" % (self.get_symbol(), self.is_updating()))
        self.set_updating(True)

        if self.start_pair.is_updating():
            while True:
                if self.start_pair.is_updating():
                    continue
                break
        else:
            self.start_pair.load_offers()

        if self.middle_pair.is_updating():
            while True:
                if self.middle_pair.is_updating():
                    continue
                break
        else:
            self.middle_pair.load_offers()

        if self.end_pair.is_updating():
            while True:
                if self.end_pair.is_updating():
                    continue
                break
        else:
            self.end_pair.load_offers()

        times = (self.start_pair.get_orderbook().get_timestamp(), self.middle_pair.get_orderbook().get_timestamp(),
                 self.end_pair.get_orderbook().get_timestamp())

        first = min(times)
        latest = max(times)

        self.timestamp = latest
        self.spread = self.timestamp - first

        if self.spread > 5:
            return self.set_updating(False)

        best_amount = self.get_best_amount()
        if best_amount:
            self.win(best_amount)
        self.set_updating(False)

        """
        Check if win is possible another time
        """
        if best_amount:
            self.update()

    def win(self, calc):
        """
        Found win, print and execute
        :param calc: information from
        :return:
        """
        win = calc[0]
        amount = calc[1]
        percentage = win/amount * 100
        API.log.log_and_print("equalizer_win.txt", "%s use %16.8f %s to make %16.8f %s (%.3f%%) orderbook spread: %.3fs" %
              (self.ticker, amount / pow(10, self.outer_currency.get_decimals()), self.outer_currency.get_name(),
               win / pow(10, self.outer_currency.get_decimals()), self.outer_currency.get_name(), percentage,
               self.get_spread()))

        for trade in calc[3]:
            API.log.log_and_print("equalizer_win.txt", trade)

        if not self.view_only:
            self.execute(calc[3])
        self.reset_blocked()
        return

    def calc(self, amount):
        try:
            all_trades = []
            trades, amount = self.start_pair.get_orderbook().taker(amount, self.outer_currency)
            all_trades.append(Trade.combine(trades))
            trades, amount = self.middle_pair.get_orderbook().taker(all_trades[0].get_want(), self.inner_first_currency)
            all_trades.append(Trade.combine(trades))
            trades, amount = self.end_pair.get_orderbook().taker(all_trades[1].get_want(), self.inner_second_currency)
            all_trades.append(Trade.combine(trades))
            return all_trades[2].get_want(), all_trades
        except KeyError:
            return 0, []

    def get_spread(self):
        return self.spread

    def get_best_amount(self):

        best_win = []
        i = 0
        run = True
        while run:
            try:
                start_market = self.start_pair.get_orderbook()
                middle_market = self.middle_pair.get_orderbook()
                end_market = self.end_pair.get_orderbook()
                max_possible_start = start_market.get_sum_after_fees(i, start_market.get_maker_trade_way(self.outer_currency), self.inner_first_currency)
                max_possible_middle = middle_market.get_sum(i, middle_market.get_maker_trade_way(self.inner_first_currency), self.inner_first_currency)
                balance = self.outer_currency.get_balance()
                """
                Only use 90% if SWTH to remain enough for paying fees
                """
                if self.outer_currency == self.start_pair.get_exchange().get_fee_token():
                    balance = balance * 0.9

                if not max_possible_start or not max_possible_middle:
                    break

                if max_possible_start > max_possible_middle:
                    max_possible_start = max_possible_middle

                if self.start_pair.get_exchange().get_minimum_amount(self.inner_first_currency) > max_possible_start:
                    i = i + 1
                    continue

                max_possible_middle = middle_market.get_sum_after_fees(i, middle_market.get_maker_trade_way(self.inner_first_currency), self.inner_second_currency)
                max_possible_end = end_market.get_sum(i, end_market.get_maker_trade_way(self.inner_second_currency), self.inner_second_currency)

                if not max_possible_middle or not max_possible_end:
                    break

                if max_possible_middle > max_possible_end:
                    max_possible_middle = max_possible_end
                    if self.start_pair.get_exchange().get_minimum_amount(self.inner_second_currency) > max_possible_middle:
                        i = i + 1
                        continue
                    tmp = self.middle_pair.get_orderbook().reverse_taker(max_possible_middle, self.inner_first_currency)
                    if tmp < max_possible_start:
                        max_possible_start = tmp

                start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outer_currency)
                if not self.view_only and start_with > balance:
                    if balance < self.start_pair.get_exchange().get_minimum_amount(self.outer_currency):
                        return
                    start_with = balance
                if start_with == 0:
                    break
                end_with, trades = self.calc(start_with)

                win = end_with-start_with

                percentage = win/start_with * 100
                log_string = ":%s:%.8f (%.2f%%) time spread:%.3fs\n" % (self.get_symbol(),
                                                                     win/pow(10, self.outer_currency.get_decimals()),
                                                                     percentage, self.get_spread())

                for trade in trades:
                    log_string = log_string + str(trade) + "\n"
                API.log.log("equalizer_all.txt", log_string)

                if win > 0:
                    for trade in trades:
                        pair = trade.get_pair()
                        exchange = pair.get_exchange()
                        if pair.is_blocked():
                            return
                        if exchange.get_minimum_amount(pair.get_base_token()) > trade.get_amount_base():
                            return
                        if exchange.get_minimum_amount(pair.get_quote_token()) > trade.get_amount_quote():
                            return

                    best_win.append((win, start_with, end_with, trades))
                else:
                    API.log.log("update.txt", "%s break" % self.get_symbol())
                    if percentage > -10:
                        log_string = "%s:%.8f (%.2f%%) time spread:%.3fs\n" % (self.get_symbol(),
                                                                               win/pow(10, self.outer_currency.get_decimals()),
                                                                               percentage, self.get_spread())

                        for trade in trades:
                            log_string = log_string + str(trade) + "\n"
                        API.log.log("equalizer_almost.txt", log_string)

                    break
                i = i + 1
            except Exception as e:
                print(e)
                print(self.get_symbol())
                break

        if len(best_win) > 0:
            best_win = sorted(best_win, key=lambda entry: entry[0], reverse=True)
            return best_win[0]

    def get_symbol(self):
        return self.ticker

    @staticmethod
    def get_all_equalizer(pairs, start_with=None, view_only=True):
        equalizers = []
        for start_pair in pairs:
            for middle_pair in pairs:
                for end_pairs in pairs:
                    try:
                        eq = Equalizer(start_pair, middle_pair, end_pairs, start_with)
                        eq.toggle_view_only(view_only)
                        equalizers.append(eq)
                    except ValueError:
                        continue
        return equalizers

    def execute(self, trades):
        API.log.log("execute.txt", self.get_symbol())
        for trade in trades:
            trade.get_pair().set_blocked(True)
            API.log.log("execute.txt", "%s" % trade)
            order_details = trade.send_order()
            trade.get_pair().set_blocked(False)
            if not order_details:
                return

    def reset_blocked(self):
        self.start_pair.set_blocked(False)
        self.middle_pair.set_blocked(False)
        self.end_pair.set_blocked(False)
