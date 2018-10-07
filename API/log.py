
import os
import time


def log(filename, text):
    path = "logs/mainnet/"
    if not os.path.isdir("logs/"):
        os.makedirs("logs/")

    if not os.path.isdir("logs/testnet/"):
        os.makedirs("logs/testnet/")

    if not os.path.isdir("logs/mainnet/"):
        os.makedirs("logs/mainnet/")

    f = open(path+filename, "a")
    f.write(time.strftime('[%Y-%m-%d %H:%M:%S]:', time.localtime(time.time()))+str(text)+"\n")
    f.flush()
    f.close()


def log_and_print(filename, text):
    log(filename, text)
    print(text)
