import API.api_request as request

from API.contract import Contract
from API.token import Token
from API.pair import Pair
from API.candlestick import Candlestick
from equalizer import Equalizer

import time


class Switcheo(object):

    _API_URL = [
        "https://api.switcheo.network",
        "https://test-api.switcheo.network"
    ]

    MAIN_NET = 0
    TEST_NET = 1

    def __init__(self, api_net=MAIN_NET, fees=0.0015):
        self.url = Switcheo._API_URL[api_net]
        self.tokens = []
        self.pairs = []
        self.contracts = []
        self.fees = fees

    def initialise(self):
        self.load_contracts()
        self.load_tokens()
        self.load_pairs()
        self.load_last_prices()

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


if __name__ == "__main__":
    switcheo = Switcheo()
    switcheo.initialise()
    contract = switcheo.get_contract("NEO")
    """gas_neo = switcheo.get_pair("GAS_NEO")
    swth_gas = switcheo.get_pair("SWTH_GAS")
    swth_neo = switcheo.get_pair("SWTH_NEO")
    equalizer = Equalizer(gas_neo, swth_gas, swth_neo)
    gas_neo.load_offers(contract)
    swth_gas.load_offers(contract)
    swth_neo.load_offers(contract)"""
    equalizers = switcheo.get_all_equalizer()
    print(len(equalizers))
    print(len(switcheo.get_pairs()))
    while True:
        for pair in switcheo.get_pairs():
            pair.load_offers(contract)





