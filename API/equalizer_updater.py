'''
Created on 24.07.2018

@author: devel

Requests the order book of a trading pairs with a given amount of requests of seconds
'''
import threading
import time


class EqualizerUpdater(object):

    '''
        Creates an new OrderBookCollector with the given trading pairs.
        With rps(requests per seconds) it sends requests to respond the order book with n entries
        I takes care to do not more requests per seconds so the exchange will not close the connection
        After one round of updating the order books the collector sets a flag to finished but will continue
        updating the books.
    '''
    def __init__(self, request_pairs, rps=10):
        self.rps = rps
        self.request = request_pairs
        self.counter = 1
        self.last_request = 0
        self.stop_threads = True
        self.request_thread = []
        self.finished = False
        self.timeperiod = 1 / self.rps

    '''
        Starts the collector doing his work and creates threads for requesting the exchange
    '''
    def start(self):
        if not self.stop_threads:
            return

        self.stop_threads = False
        for i in range(0, self.rps):
            self.request_thread = self.request_thread + [threading.Thread(target=self.load_data)]
            self.request_thread[i].start()
            time.sleep(0.1)

    '''
        Sets a flag so each thread will stop next loop
    '''
    def stop(self):
        self.stop_threads = True
        while True:
            stop = True
            for t in self.request_thread:
                if t.isAlive():
                    stop = False
                    break

            if stop:
                break

    '''
        This is the function which is called from each thread and contains a loop.
        Each run it will check if the time since last request is to early to request the next order book
        If so, it will sleep and try next run.
        If all is okay it updates the last request time and sends a request to the exchange.
        Sometimes it happens that the exchange sends bad gateway(or something else) respond and
        the API throws an exception, in this case the collector will print a message and breaks this run. 
        The next thread will try again.
    '''
    def load_data(self):
        while not self.stop_threads:
            if self.last_request + self.timeperiod > time.time():
                time.sleep(self.timeperiod)
                continue

            self.last_request = time.time()

            pair = self.request[self.counter-1]

            pair.update()

            self.counter = self.counter + 1

            if self.counter > len(self.request):
                self.finished = True
                self.counter = 1


