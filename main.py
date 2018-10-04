import API.api_request as request

from API.contract import Contract
from API.token import Token
from API.pair import Pair
from API.candlestick import Candlestick
from equalizer import Equalizer

from switcheo.authenticated_client import AuthenticatedClient
from switcheo.neo.utils import *

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
        self.load_balances()

    def get_minimum_amount(self, token):
        if token.get_name() == "NEO":
            return 0.01

        if token.get_name() == "RHT":
            return 0.01

        if token.get_name() == "GAS":
            return 0.1

        return 1

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
        raw_candles = request.public_request(self.get_url(), "/v2/tickers/candlesticks")
        candlesticks = []
        timestamp = self.get_timestamp() - 1*60*60*24
        for entry in raw_candles:
            pair = self.get_pair(entry["pair"])
            if not pair:
                continue
            candlesticks.append(Candlestick(pair, timestamp, float(entry["open"]),
                                            float(entry["close"]), float(entry["high"]), float(entry["low"]),
                                            float(entry["volume"]), float(entry["quote_volume"]),
                                            Candlestick.INTERVAL_MIN_1440))
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
        raw_data = self.get_balances(self.kp, self.get_contract("NEO"))
        for name in raw_data["confirmed"]:
            balance = float(raw_data["confirmed"][name])
            token = self.get_token(name)
            if not token:
                continue
            token.set_balance(balance / pow(10, token.get_decimals()))
            print(token)

class Log(object):

    @staticmethod
    def log(filename, text):
        path = "logs/mainnet/"
        if not os.path.isdir("logs/"):
            os.makedirs("logs/")

        if not os.path.isdir("logs/testnet/"):
            os.makedirs("logs/testnet/")

        if not os.path.isdir("logs/mainnet/"):
            os.makedirs("logs/mainnet/")

        if Switcheo.API_NET == Switcheo.TEST_NET:
            path = "logs/testnet/"

        with open(path+filename, "a+") as file:
            file.write(text)




if __name__ == "__main__":


    switcheo = Switcheo()
    #switcheo = Switcheo(api_net=Switcheo.TEST_NET)
    switcheo.initialise()
    contract = switcheo.get_contract("NEO")
    print(switcheo.get_balances(switcheo.kp, contract))
    equalizers = switcheo.get_all_equalizer()

    #print(len(equalizers))
    print(switcheo.client.create_order(switcheo.kp, "SWTH_NEO", "buy", 0.00044999, 100))
    print(len(switcheo.get_pairs()))
    while True:
        for pair in switcheo.get_pairs():
            if pair.get_last_price() == 0:
                continue
            pair.load_offers(contract)







