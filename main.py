import API.api_request as request

from API.contract import Contract
from API.token import Token
from API.pair import Pair
from API.candlestick import Candlestick
from equalizer import Equalizer

from switcheo.authenticated_client import AuthenticatedClient
from switcheo.neo.utils import *

import API.log
import time
import os




class Switcheo(object):

    _API_URL = [
        "https://api.switcheo.network",
        "https://test-api.switcheo.network"
    ]

    MAIN_NET = 0
    TEST_NET = 1

    API_NET = None

    def __init__(self, api_net=MAIN_NET, fees=0.0015):
        self.url = Switcheo._API_URL[api_net]
        self.tokens = []
        self.pairs = []
        self.contracts = []
        self.fees = fees
        self.client = AuthenticatedClient(api_url=self.url)
        self.kp = open_wallet("319616b9d276944502cebf6858ec66ba79624bb50f57a4d150e72a9636115edf")
        API_NET = api_net

    def initialise(self):
        self.load_contracts()
        self.load_tokens()
        self.load_pairs()
        self.load_last_prices()
        self.load_24_hours()
        self.load_balances()

    def get_minimum_amount(self, token):
        if token.get_name() == "NEO":
            return 0.01 * pow(10, 8)

        if token.get_name() == "RHT":
            return 0.01 * pow(10, 8)

        if token.get_name() == "GAS":
            return 0.1 * pow(10, 8)

        return 1 * pow(10, 8)

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

    def get_all_equalizer(self):
        pairs = self.pairs
        equalizers = []
        for start_pair in pairs:
            for middle_pair in pairs:
                for end_pairs in pairs:
                    try:
                        equalizers.append(Equalizer(start_pair, middle_pair, end_pairs))
                    except ValueError:
                        continue
        return equalizers

    def get_balances(self, keypair, contract):
        params = {
            "addresses[]": neo_get_scripthash_from_address(keypair.GetAddress()),
            "contract_hashes[]": contract.get_latest_hash()
        }
        return request.public_request(self.get_url(), "/v2/balances", params)

    def load_balances(self):
        for token in self.tokens:
            token.set_balance(0)
        raw_data = self.get_balances(self.kp, self.get_contract("NEO"))
        for name in raw_data["confirmed"]:
            balance = float(raw_data["confirmed"][name])
            token = self.get_token(name)
            if not token:
                continue
            token.set_balance(balance)

            API.log.log("balances.txt", token)

    def get_scripthash(self):
        return neo_get_scripthash_from_address(self.kp.GetAddress())


if __name__ == "__main__":


    switcheo = Switcheo()
    switcheo.initialise()
    contract = switcheo.get_contract("NEO")
    equalizers = switcheo.get_all_equalizer()

    while True:
        try:
            for pair in switcheo.get_pairs():
                if pair.get_candlestick_24h() is None or pair.get_candlestick_24h().get_volume() == 0:
                    continue
                pair.load_offers(contract)
                time.sleep(0.1)
            switcheo.load_last_prices()
            switcheo.load_24_hours()
            switcheo.load_balances()
        except Exception as e:
            print(e)







