from API.pair import Pair
import API.log
import time
from API.trade import Trade

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
        self.spread = 0

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

        first =  min(self.start_pair.get_orderbook().get_timestamp(), self.middle_pair.get_orderbook().get_timestamp(),
                     self.end_pair.get_orderbook().get_timestamp())

        self.spread = self.timestamp - first

        self.get_best_amount()


    def printWin(self, calc):
        win =calc[0]
        amount = calc[1]
        ftime = time.strftime('%Y-%m-%d %H:%M:%S:', time.localtime(self.timestamp))
        percentage = win/amount * 100
        API.log.log_and_print("equalizer_win.txt", "[%s]%s use %16.8f %s to make %16.8f %s (%.3f%%) orderbook spread: %.3fs" %(ftime, self.ticker, amount/pow(10, self.outter_currency.get_decimals()), self.outter_currency.get_name(),
                                                         win/pow(10, self.outter_currency.get_decimals()), self.outter_currency.get_name(), percentage, self.get_spread()))

        for trade in calc[3]:
            API.log.log_and_print("equalizer_win.txt", str(trade))
        """try:
            self.execute(calc[3])
        except Exception as e:
            print(e)"""
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

                max_possible_middle = middle_market.get_sum_after_fees(i, middle_market.get_maker_trade_way(self.inner_first_currency), self.inner_second_currency)
                max_possible_end = end_market.get_sum(i, end_market.get_maker_trade_way(self.inner_second_currency), self.inner_second_currency)

                if not max_possible_middle or not max_possible_end:
                    break

                if max_possible_middle > max_possible_end:
                    max_possible_middle = max_possible_end
                    tmp = self.middle_pair.get_orderbook().reverse_taker(max_possible_middle, self.inner_first_currency)
                    if tmp < max_possible_start:
                        max_possible_start = tmp

                start_with = self.start_pair.get_orderbook().reverse_taker(max_possible_start, self.outter_currency)
                if start_with == 0:
                    break
                end_with, trades = self.calc(start_with)

                win = end_with-start_with

                percentage = win/start_with * 100

                API.log.log("equalizer_all.txt", "%s:%.8f (%.2f%%) time spread:%.3fs" %
                            (self.get_symbol(),
                             win/pow(10, self.outter_currency.get_decimals()),
                             percentage, self.get_spread()))
                for trade in trades:
                    API.log.log("equalizer_all.txt", "%s" % trade)

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
                        API.log.log("equalizer_almost.txt", "%s:%.8f (%.2f%%)" % (self.get_symbol(), win/pow(10, self.outter_currency.get_decimals()), percentage))
                        for trade in trades:
                            API.log.log("equalizer_almost.txt", "%s" % trade)
                    break
                i = i + 1
            except Exception as e:
                print(e)
                break

        if len(best_win) > 0:
            best_win = sorted(best_win, key=lambda entry: entry[0], reverse=True)
            self.calc(best_win[0][1])
            self.printWin(best_win[0])

    def get_symbol(self):
        return self.ticker

    def execute(self, trades):
        for trade in trades:

            pair = trade.get_pair()
            origin_currency = pair.get_quote_token()
            target_currency = pair.get_base_token()
            way = trade.get_way()
            way_string = "buy"
            if way == Trade.WAY_BUY:
                origin_currency = pair.get_base_token()
                target_currency = pair.get_quote_token()
                way_string = "sell"

            if origin_currency.get_balance() < pair.get_exchange().get_minimum_amount(origin_currency):
                return

            want_amount = trade.get_offer()
            offer_amount = trade.get_want()
            price = float("%.8f" % trade.get_price())

            if offer_amount > origin_currency.get_balance():
                want_amount = int(origin_currency.get_balance()/offer_amount * want_amount)

            API.log.log("execute.txt", "price before: %.8f, offer amount before: %s" % (price, offer_amount))
            """
            reduce risk of not enough balance
            """
            """if way == Trade.WAY_SELL:
                want_amount = int(offer_amount / price)
                offer_amount = int(want_amount*price)
                price = float("%.8f" % (offer_amount/want_amount))
            else:
                want_amount = int(price * offer_amount)
                offer_amount = int(want_amount/price)
                price = float("%.8f" % (offer_amount/want_amount))"""

            API.log.log("execute.txt", "price after: %.8f, offer amount after: %s" % (price, offer_amount))



            #TODO workaround
            offer_amount = offer_amount / pow(10, 8)
            want_amount = want_amount / pow(10, 8)

            API.log.log("execute.txt", "%s: %s price:%.8f %.8f" % (pair.get_symbol(), trade.get_trade_block().lower(), price, offer_amount))

            try:
                order_details = trade.get_pair().get_exchange().client.create_order(pair.get_exchange().kp, pair.get_symbol(),
                                                                     trade.get_trade_block().lower(), price,
                                                                     want_amount)
                API.log.log_and_print("execute_order.txt", str(order_details))
                fill_offer = 0
                fill_want = 0
                for fills in order_details["fills"]:
                    print(fills)
                    fill_offer = int(fill_offer + float(fills["fill_amount"]))
                    fill_want = int(fill_want + float(fills["want_amount"]))
                offer_amount = int(offer_amount * pow(10,8))
                want_amount = int(want_amount * pow(10,8))

                API.log.log_and_print("execute_order.txt", "%s %s %s" % (fill_offer, offer_amount,  fill_offer/offer_amount*100))
                API.log.log_and_print("execute_order.txt", "%s %s %s" % (fill_want, want_amount,  fill_want/want_amount*1))
                if fill_want/want_amount*100 > 0.98 and fill_offer/offer_amount*100 <= 100:
                    r = trade.get_pair().get_exchange().client.execute_order(order_details, pair.get_exchange().kp)
                    API.log.log_and_print("execute_order.txt", "Response: %s" %r)
                    loaded = trade.get_pair().get_exchange().client.get_orders(self, trade.get_pair().get_exchange().get_scripthash(), pair=pair.get_symbol())
                    API.log.log_and_print("execute_order.txt", "load order: %s" % loaded)
                    pair.get_orderbook().set_timestamp(0)
                    trade.get_pair().get_exchange().load_balances()


            except Exception as e:
                print(e)
                return
        trades[0].get_pair().get_exchange().load_balances()
