import os
import time


def log(filename, text):
    """
    Writes text to file in logs/mainnet/filename and adds a timestamp
    :param filename: filename
    :param text: text
    :return: None
    """
    path = "logs/mainnet/"
    if not os.path.isdir("logs/"):
        os.makedirs("logs/")

    if not os.path.isdir("logs/mainnet/"):
        os.makedirs("logs/mainnet/")

    f = open(path+filename, "a")
    f.write(time.strftime('[%Y-%m-%d %H:%M:%S]:', time.localtime(time.time()))+str(text)+"\n")
    f.flush()
    f.close()


def log_and_print(filename, text):
    """
    Writes text to file in logs/mainnet/filename, adds a timestamp and prints the same to the console
    :param filename: filename
    :param text: text
    :return: None
    """
    log(filename, text)
    print(time.strftime('[%Y-%m-%d %H:%M:%S]:', time.localtime(time.time()))+str(text))
