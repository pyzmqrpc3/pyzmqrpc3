

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread


class ZmqProxyThread(Thread):

    def __init__(self):
        super().__init__()

        self.proxy = None

    def get_last_received_message(self):
        if self.proxy:
            return self.proxy.get_last_received_message()
        return None

    def run(self):
        if self.proxy:
            self.proxy.run()

    def stop(self):
        if self.proxy:
            self.proxy.stop()
