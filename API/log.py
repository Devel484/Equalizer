
import os


def log(filename, text):
    path = "logs/mainnet/"
    if not os.path.isdir("logs/"):
        os.makedirs("logs/")

    if not os.path.isdir("logs/testnet/"):
        os.makedirs("logs/testnet/")

    if not os.path.isdir("logs/mainnet/"):
        os.makedirs("logs/mainnet/")

    f = open(path+filename, "a")
    f.write(str(text)+"\n")
    f.flush()
    f.close()
