
import API.log
import time
from API.trade import Trade
from API.switcheo import Switcheo
from API.offerbook_collector import OfferbookCollector


class Equalizer(object):

    def __init__(self, start_pair, middle_pair, end_pair, start_with=None):
        self.outter_currency = start_pair.get_equal_token(end_pair)
        self.inner_first_currency = start_pair.get_equal_token(middle_pair)
        self.inner_second_currency = middle_pair.get_equal_token(end_pair)
        if self.outter_currency is None or \
                self.inner_first_currency is None or \
                self.inner_second_currency is None or \
                start_pair == middle_pair or \
                middle_pair == end_pair or \
                start_pair == end_pair or \
                (start_with is not None and start_with != self.outter_currency) or \
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
        #start_pair.add_on_update(self.update)
        self.middle_pair = middle_pair
        #middle_pair.add_on_update(self.update)
        self.end_pair = end_pair
        #end_pair.add_on_update(self.update)

        self.start_market = start_pair.get_orderbook()
        self.middle_market = middle_pair.get_orderbook()
        self.end_market = end_pair.get_orderbook()

        self.total_win = 0
        self.last = 0
        self.timestamp = 0
        self.spread = 0
        self.updating = False

    def get_start_token(self):
        return self.outter_currency

    def is_updating(self):
        return self.updating

    def set_updating(self, b):
        self.updating = b

    def update(self):
        if self.is_updating():
            return
        self.set_updating(True)
        self.start_pair.load_offers()
        self.middle_pair.load_offers()
        self.end_pair.load_offers()
        if not self.start_pair.is_updated():
            return

        if not self.middle_pair.is_updated():
            return

        if not self.end_pair.is_updated():
            return

        """if self.start_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.start_pair.get_orderbook().get_timestamp()

        if self.middle_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.middle_pair.get_orderbook().get_timestamp()

        if self.end_pair.get_orderbook().get_timestamp() > self.timestamp:
            self.timestamp = self.end_pair.get_orderbook().get_timestamp()"""

        times = (self.start_pair.get_orderbook().get_timestamp(), self.middle_pair.get_orderbook().get_timestamp(),
                 self.end_pair.get_orderbook().get_timestamp())

        first = min(times)
        latest = max(times)

        self.timestamp = latest
        self.spread = self.timestamp - first

        self.get_best_amount()
        self.set_updating(False)

    def print_win(self, calc):
        win = calc[0]
        amount = calc[1]
        percentage = win/amount * 100
        API.log.log_and_print("equalizer_win.txt", "%s use %16.8f %s to make %16.8f %s (%.3f%%) orderbook spread: %.3fs" %
              (self.ticker, amount/pow(10, self.outter_currency.get_decimals()), self.outter_currency.get_name(),
               win/pow(10, self.outter_currency.get_decimals()), self.outter_currency.get_name(), percentage,
               self.get_spread()))

        for trade in calc[3]:
            API.log.log_and_print("equalizer_win.txt", trade)

        self.execute(calc[3])
        return

    def calc(self, amount):
        try:
            all_trades = []
            trades, amount = self.start_pair.get_orderbook().taker(amount, self.outter_currency)
            all_trades.append(Trade.combine(trades))
            trades, amount = self.middle_pair.get_orderbook().taker(amount, self.inner_first_currency)
            all_trades.append(Trade.combine(trades))
            trades, amount = self.end_pair.get_orderbook().taker(amount, self.inner_second_currency)
            all_trades.append(Trade.combine(trades))
            return amount, all_trades
        except KeyError:
            return 0, []

    def get_spread(self):
        return self.spread

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

                start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outter_currency)
                if start_with == 0:
                    break
                end_with, trades = self.calc(start_with)

                win = end_with-start_with

                percentage = win/start_with * 100
                log_string = "%s:%.8f (%.2f%%) time spread:%.3fs\n" % (self.get_symbol(),
                                                                     win/pow(10, self.outter_currency.get_decimals()),
                                                                     percentage, self.get_spread())

                """API.log.log("equalizer_all.txt", "%s:%.8f (%.2f%%) time spread:%.3fs" %
                            (self.get_symbol(),
                             win/pow(10, self.outter_currency.get_decimals()),
                             percentage, self.get_spread()))"""
                for trade in trades:
                    #API.log.log("equalizer_all.txt", "%s" % trade)
                    log_string = log_string + str(trade) + "\n"
                API.log.log("equalizer_all.txt", log_string)

                if win > 0:
                    for trade in trades:
                        pair = trade.get_pair()
                        exchange = pair.get_exchange()
                        if exchange.get_minimum_amount(pair.get_base_token()) > trade.get_amount_base():
                            return
                        if exchange.get_minimum_amount(pair.get_quote_token()) > trade.get_amount_quote():
                            return

                    best_win.append((win, start_with, end_with, trades))
                else:
                    if percentage > -10:
                        log_string = "%s:%.8f (%.2f%%) time spread:%.3fs\n" % (self.get_symbol(),
                                                                               win/pow(10, self.outter_currency.get_decimals()),
                                                                               percentage, self.get_spread())

                        for trade in trades:
                            log_string = log_string + str(trade) + "\n"
                        API.log.log("equalizer_almost.txt", log_string)
                        break
                i = i + 1
            except Exception as e:
                print(e)
                break

        if len(best_win) > 0:
            best_win = sorted(best_win, key=lambda entry: entry[0], reverse=True)
            self.print_win(best_win[0])

    def get_symbol(self):
        return self.ticker

    @staticmethod
    def get_all_equalizer(pairs, start_with=None):
        equalizers = []
        for start_pair in pairs:
            for middle_pair in pairs:
                for end_pairs in pairs:
                    try:
                        eq = Equalizer(start_pair, middle_pair, end_pairs, start_with)
                        equalizers.append(eq)
                    except ValueError:
                        continue
        return equalizers

    def execute(self, trades):
        for trade in trades:

            pair = trade.get_pair()
            exchange = pair.get_exchange()
            origin_currency = pair.get_quote_token()
            target_currency = pair.get_base_token()
            way = trade.get_way()
            if way == Trade.WAY_BUY:
                origin_currency = pair.get_base_token()
                target_currency = pair.get_quote_token()

            if origin_currency.get_balance() < exchange.get_minimum_amount(origin_currency):
                return

            want_amount = trade.get_want()
            offer_amount = trade.get_offer()

            if offer_amount > origin_currency.get_balance():
                want_amount = int(origin_currency.get_balance()/offer_amount * want_amount)
                if way == Trade.WAY_BUY:
                    trade = Trade(trade.get_pair(), trade.get_way(), trade.get_price(), want_amount,
                                  offer_amount, trade.get_timestamp())
                else:
                    trade = Trade(trade.get_pair(), trade.get_way(), trade.get_price(), offer_amount,
                                  want_amount, trade.get_timestamp())

            API.log.log("execute.txt", "%s" % trade)

            try:
                order_details = exchange.send_order(trade)
                API.log.log_and_print("execute_order.txt", str(order_details))
                if not order_details:
                    return
                target_currency.add_balance(want_amount)

            except Exception as e:
                API.log.log("execute.txt", "%s" % e)
                API.log.log("execute.txt", "%s" % pair.get_orderbook())
                return



if __name__ == "__main__":

    print("Equalizer searches for instant profits with the perfect amount.")
    print("If instant profit is found it will printed to the console, keep waiting")
    print("Use 'tail -f logs/mainnet/equalizer_all.txt' (only linux) to see all results even losses.")
    print("Only trades with profit will be printed.")
    switcheo = Switcheo(private_key="319616b9d276944502cebf6858ec66ba79624bb50f57a4d150e72a9636115edf")
    switcheo.initialise()
    contract = switcheo.get_contract("NEO")
    equalizers = Equalizer.get_all_equalizer(switcheo.get_pairs(), switcheo.get_token("NEO"))


    #trade = Trade(switcheo.get_pair("MCT_NEO"), Trade.WAY_BUY, 0.00014000, 10000000, 60000000, None)
    #switcheo.send_order(trade)

    offerbook_collector = OfferbookCollector(equalizers)

    offerbook_collector.start()
    print("Start loading")
    while True:
        try:
            time.sleep(10)
            switcheo.load_last_prices()
            switcheo.load_24_hours()
            switcheo.load_balances()
        except Exception as e:
            print(e)
