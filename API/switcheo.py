import API.api_request as request

from API.contract import Contract
from API.token import Token
from API.pair import Pair
from API.trade import Trade
from API.candlestick import Candlestick
import API.log

from switcheo.authenticated_client import AuthenticatedClient
from neocore.KeyPair import KeyPair
from switcheo.neo.utils import neo_get_scripthash_from_private_key
from requests.exceptions import HTTPError


class Switcheo(object):

    _API_URL = [
        "https://api.switcheo.network",
        "https://test-api.switcheo.network"
    ]

    MAIN_NET = 0
    TEST_NET = 1

    API_NET = None

    def __init__(self, api_net=MAIN_NET, fees=0.0015, private_key=None):
        self.url = Switcheo._API_URL[api_net]
        self.tokens = []
        self.pairs = []
        self.contracts = []
        self.fees = fees
        self.key_pair = None
        self.client = AuthenticatedClient(api_url=self.url)
        if private_key:
            self.key_pair = KeyPair(bytes.fromhex(private_key))

    def initialise(self):
        self.load_contracts()
        self.load_tokens()
        self.load_pairs()
        self.load_last_prices()
        self.load_24_hours()
        self.load_balances()

    @staticmethod
    def get_minimum_amount(token):
        if token.get_name() == "NEO":
            return 0.01 * pow(10, 8)

        if token.get_name() == "RHT":
            return 0.01 * pow(10, 8)

        if token.get_name() == "GAS":
            return 0.1 * pow(10, 8)

        return 1 * pow(10, 8)

    def get_key_pair(self):
        return self.key_pair

    def get_fees(self):
        return self.fees

    def get_url(self):
        return self.url

    def get_timestamp(self):
        return int(request.public_request(self.url, "/v2/exchange/timestamp")["timestamp"])/1000

    def load_contracts(self):
        raw_contracts = request.public_request(self.url, "/v2/exchange/contracts")
        self.contracts = []
        for key in raw_contracts:
            self.contracts.append(Contract(key, raw_contracts[key]))
        return self.contracts

    def get_contracts(self):
        return self.contracts

    def get_contract(self, blockchain="NEO"):
        for contract in self.contracts:
            if contract.get_chain() == blockchain:
                return contract
        return None

    def load_tokens(self):
        raw_tokens = request.public_request(self.url, "/v2/exchange/tokens")
        self.tokens = []
        for key in raw_tokens:
            self.tokens.append(Token(key, raw_tokens[key]["decimals"], raw_tokens[key]["hash"]))
        return self.tokens

    def get_tokens(self):
        return self.tokens

    def get_token(self, name):
        for token in self.tokens:
            if token.get_name() == name:
                return token
        return None

    def load_pairs(self, bases=None):
        params = None
        if bases:
            params = {"bases": bases}
        raw_pairs = request.public_request(self.url, "/v2/exchange/pairs", params)
        self.pairs = []
        for val in raw_pairs:
            quote, base = val.split("_")
            self.pairs.append(Pair(self, self.get_token(quote), self.get_token(base)))
        return self.pairs

    def get_pairs(self):
        return self.pairs

    def get_pair(self, symbol):
        for pair in self.pairs:
            if pair.get_symbol() == symbol:
                return pair
        return None

    def load_24_hours(self):
        raw_candles = request.public_request(self.get_url(), "/v2/tickers/last_24_hours")
        candlesticks = []
        timestamp = self.get_timestamp() - 1*60*60*24
        for token in self.tokens:
            token.set_volume(0)
        for entry in raw_candles:
            pair = self.get_pair(entry["pair"])
            if not pair:
                continue
            candlestick = Candlestick(pair, timestamp, float(entry["open"]),
                                      float(entry["close"]), float(entry["high"]), float(entry["low"]),
                                      float(entry["volume"]), float(entry["quote_volume"]),
                                      Candlestick.INTERVAL_MIN_1440)
            candlesticks.append(candlestick)
            pair.set_candlestick_24h(candlestick)
            pair.get_base_token().add_volume(candlestick.get_base_volume())
            pair.get_quote_token().add_volume(candlestick.get_quote_volume())
        return candlesticks

    def load_last_prices(self):
        prices = request.public_request(self.get_url(), "/v2/tickers/last_price")
        for quote in prices:
            for base in prices[quote]:
                pair = self.get_pair(quote+"_"+base)
                if not pair:
                    continue
                pair.set_last_price(float(prices[quote][base]))

        return prices

    def load_balances(self):
        params = {
            "addresses": neo_get_scripthash_from_private_key(self.key_pair.PrivateKey),
            "contract_hashes": self.get_contract("NEO").get_latest_hash()
        }

        raw_balances = request.public_request(self.get_url(), "/v2/balances", params)
        for token in self.tokens:
            token.set_balance(0)

        for name in raw_balances["confirmed"]:
            token = self.get_token(name)
            token.set_balance(int(float(raw_balances["confirmed"][name])))

    def load_orders(self, pair=None):
        pair_name = ""
        if pair:
            pair_name = pair.get_symbol()
        params = {
            "address": neo_get_scripthash_from_private_key(self.key_pair.PrivateKey),
            "contract_hash": self.get_contract("NEO").get_latest_hash(),
            "pair": pair_name
        }

        return request.public_request(self.get_url(), "/v2/orders", params)



    def send_order(self, trade):
        want_amount = trade.get_want() / pow(10, 8)
        price = trade.get_price()
        try:
            order_details = self.client.create_order(self.key_pair, trade.get_pair().get_symbol(),
                                                     trade.get_trade_way_as_string().lower(), price, want_amount, False)

        except HTTPError as e:
            API.log.log_and_print("API_response:", "[%s]:(%s):%s" % (e.response.status_code, e.response.url,
                                                                     e.response.text))
            want_amount = int(trade.get_want() / pow(10, 2)) / pow(10, 6)
            API.log.log_and_print("execute.txt", "Changed amount: %.8f pair: %s" % (want_amount, trade.get_pair().get_symbol()))
            order_details = self.client.create_order(self.key_pair, trade.get_pair().get_symbol(),
                                                     trade.get_trade_way_as_string().lower(), price, want_amount, False)

        fill_want = 0
        fee_amount = 0
        for fills in order_details["fills"]:
            fill_want = int(fill_want + float(fills["want_amount"]))
            fee_amount = int(fee_amount + float(fills["fee_amount"]))

        target_currency = trade.get_pair().get_base_token()
        way = trade.get_way()
        if way == Trade.WAY_BUY:
            target_currency = trade.get_pair().get_quote_token()

        accept_want = int(want_amount * pow(10, 8)*0.98)

        API.log.log_and_print("execute_order.txt", "%s von %s (%.3f)" % (fill_want, want_amount * pow(10, 8), fill_want/(want_amount * pow(10, 8))*100))
        if accept_want <= fill_want:

            order_details = self.client.execute_order(order_details, self.key_pair)
            #API.log.log_and_print("execute_order.txt", order_details)
            while True:
                self.load_balances()
                if target_currency.get_balance() >= fill_want - fee_amount:
                    break
            return order_details



