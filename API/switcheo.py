"""
author: Devel484
"""
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
        """
        Create new Switcheo exchange with url, fee rate and private key
        :param api_net:
        :param fees:
        :param private_key:
        """
        self.url = Switcheo._API_URL[api_net]
        self.tokens = []
        self.pairs = []
        self.contracts = []
        self.fees = fees
        self.key_pair = None
        self.client = AuthenticatedClient(api_url=self.url)
        if private_key:
            try:
                self.key_pair = KeyPair(bytes.fromhex(private_key))
            except:
                self.key_pair = None
                print("No or incorrect private key. Equalizer changes to view only mode")

    def initialise(self):
        """
        Initialise exchange by loading some data.
        :return: None
        """
        self.load_contracts()
        self.load_tokens()
        self.load_pairs()
        self.load_last_prices()
        self.load_24_hours()
        self.load_balances()

    @staticmethod
    def get_minimum_amount(token):
        """
        Get minimum trading amount of token
        :param token:
        :return:
        """
        if token.get_name() == "NEO":
            return 0.01 * pow(10, 8)

        if token.get_name() == "RHT":
            return 0.01 * pow(10, 8)

        if token.get_name() == "GAS":
            return 0.1 * pow(10, 8)

        return 1 * pow(10, 8)

    def get_key_pair(self):
        """
        :return: Neo Key Pair
        """
        return self.key_pair

    def get_fees(self):
        """
        :return: fee rate
        """
        return self.fees

    def get_url(self):
        """
        :return: basic URL
        """
        return self.url

    def get_timestamp(self):
        """
        :return: timestamp in seconds
        """
        return int(request.public_request(self.url, "/v2/exchange/timestamp")["timestamp"])/1000

    def load_contracts(self):
        """
        Load contracts and creates objects
        :return: list of objects
        """
        raw_contracts = request.public_request(self.url, "/v2/exchange/contracts")
        if not raw_contracts:
            return
        self.contracts = []
        for key in raw_contracts:
            self.contracts.append(Contract(key, raw_contracts[key]))
        return self.contracts

    def get_contracts(self):
        """
        :return: contracts
        """
        return self.contracts

    def get_contract(self, blockchain="NEO"):
        """
        Get contract of blockchain
        :param blockchain: blockchain name
        :return: contract
        """
        for contract in self.contracts:
            if contract.get_blockchain() == blockchain:
                return contract
        return None

    def load_tokens(self):
        """
        Load all tokens from exchange and create objects
        :return: list of tokens
        """
        raw_tokens = request.public_request(self.url, "/v2/exchange/tokens")
        if not raw_tokens:
            return
        self.tokens = []
        for key in raw_tokens:
            self.tokens.append(Token(key, raw_tokens[key]["decimals"], raw_tokens[key]["hash"]))
        return self.tokens

    def get_tokens(self):
        """
        :return: tokens
        """
        return self.tokens

    def get_token(self, name):
        """
        :param name: name of token
        :return: token
        """
        for token in self.tokens:
            if token.get_name() == name:
                return token
        return None

    def load_pairs(self, bases=None):
        """
        Load all pairs from exchange(with bases)
        :param bases: i.e. NEO, SWTH, ...
        :return: List of objects
        """
        params = None
        if bases:
            params = {"bases": bases}
        raw_pairs = request.public_request(self.url, "/v2/exchange/pairs", params)
        if not raw_pairs:
            return
        self.pairs = []
        for val in raw_pairs:
            quote, base = val.split("_")
            quote_token = self.get_token(quote)
            base_token = self.get_token(base)
            if not quote_token or not base_token:
                continue
            self.pairs.append(Pair(self, quote_token, base_token))
        return self.pairs

    def get_pairs(self):
        """
        :return: pairs
        """
        return self.pairs

    def get_pair(self, symbol):
        """
        Get pair with symbol i.e. SWTH_NEO
        :param symbol: symbol
        :return: pair
        """
        for pair in self.pairs:
            if pair.get_symbol() == symbol:
                return pair
        return None

    def load_24_hours(self):
        """
        Load 24h candlestick for each pair
        :return: list of objects
        """
        raw_candles = request.public_request(self.get_url(), "/v2/tickers/last_24_hours")
        if not raw_candles:
            return
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
        """
        Load price of each pair
        :return: list of prices
        """
        prices = request.public_request(self.get_url(), "/v2/tickers/last_price")
        if not prices:
            return
        for quote in prices:
            for base in prices[quote]:
                pair = self.get_pair(quote+"_"+base)
                if not pair:
                    continue
                pair.set_last_price(float(prices[quote][base]))

        return prices

    def load_balances(self):
        """
        Load all balances from the exchange and updates them in the tokens
        :return: balances
        """
        if self.get_key_pair() is None:
            return []
        params = {
            "addresses": neo_get_scripthash_from_private_key(self.key_pair.PrivateKey),
            "contract_hashes": self.get_contract("NEO").get_latest_hash()
        }

        raw_balances = request.public_request(self.get_url(), "/v2/balances", params)
        if not raw_balances:
            return
        for token in self.tokens:
            token.set_balance(0)

        for name in raw_balances["confirmed"]:
            token = self.get_token(name)
            token.set_balance(int(float(raw_balances["confirmed"][name])))
        return raw_balances

    def load_orders(self, pair=None):
        """
        Load all orders
        :param pair: orders from pair
        :return: orders
        """
        pair_name = ""
        if pair:
            pair_name = pair.get_symbol()
        params = {
            "address": neo_get_scripthash_from_private_key(self.key_pair.PrivateKey),
            "contract_hash": self.get_contract("NEO").get_latest_hash(),
            "pair": pair_name
        }

        orders = request.public_request(self.get_url(), "/v2/orders", params)
        if not orders:
            return
        return orders

    def send_order(self, trade):
        """
        Send and order to the exchange and executes it
        :param trade: executing trade
        :return: order details
        """
        if not self.get_key_pair():
            return None

        price = trade.get_price()

        """
        Try to get amount, if not possible reduce precision
        """
        order_details = None
        want_amount = 0
        for i in range(3):
            want_amount = int(trade.get_want() / pow(10, i)) / pow(10, 8-i)
            API.log.log_and_print("execute.txt", "Want amount: %.8f pair: %s" % (want_amount, trade.get_pair().get_symbol()))
            order_details = self.client.create_order(self.key_pair, trade.get_pair().get_symbol(),
                                                     trade.get_trade_way_as_string().lower(), price, want_amount, False)
            if order_details:
                break

        if not order_details:
            API.log.log_and_print("execute.txt", "Not possible to get valid order details for pair: %s" % trade.get_pair().get_symbol())
            return

        fill_want = 0
        fee_amount = 0
        for fills in order_details["fills"]:
            fill_want = int(fill_want + float(fills["want_amount"]))
            fee_amount = int(fee_amount + float(fills["fee_amount"]))

        target_currency = trade.get_pair().get_base_token()
        way = trade.get_way()
        if way == Trade.WAY_BUY:
            target_currency = trade.get_pair().get_quote_token()

        API.log.log_and_print("execute_order.txt", "%s von %s (%.3f)" % (fill_want, want_amount * pow(10, 8), fill_want/(want_amount * pow(10, 8))*100))

        order_details = self.client.execute_order(order_details, self.key_pair)
        if not order_details:
            API.log.log_and_print("execute.txt", "Not possible to get valid executing order details for pair: %s" % trade.get_pair().get_symbol())
            return
        while True:
            self.load_balances()
            if target_currency.get_balance() >= fill_want - fee_amount:
                break
        return order_details



