from API.switcheo import Switcheo
from equalizer import Equalizer
from API.equalizer_updater import EqualizerUpdater

import time

PRIVATE_KEY = "INSERT YOUR PRIVATE KEY HERE"

def main():
    print("Equalizer searches for instant profits with the perfect amount.")
    print("If instant profit is found it will printed to the console, keep waiting")
    print("Use 'tail -f logs/mainnet/equalizer_all.txt' (only linux) to see all results even losses.")
    print("Only trades with profit will be printed.")

    switcheo = Switcheo(private_key=PRIVATE_KEY)
    switcheo.initialise()

    equalizers = Equalizer.get_all_equalizer(switcheo.get_pairs(), switcheo.get_token("NEO"), switcheo.get_key_pair() is None)
    equalizers = equalizers + Equalizer.get_all_equalizer(switcheo.get_pairs(), switcheo.get_token("SWTH"), switcheo.get_key_pair() is None)

    equalizer_updater = EqualizerUpdater(equalizers)

    equalizer_updater.start()
    print("Start loading")
    while True:
        try:
            time.sleep(10)
            switcheo.load_last_prices()
            switcheo.load_24_hours()
            switcheo.load_balances()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
