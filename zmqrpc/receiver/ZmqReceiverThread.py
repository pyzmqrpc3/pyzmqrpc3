

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread

from .ZmqReceiver import ZmqReceiver


class ZmqReceiverThread(Thread):

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_sub_connect_addresses=None,
            recreate_timeout=60,
            username=None,
            password=None):
        super().__init__()

        self.__receiver = ZmqReceiver(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_timeout=recreate_timeout,
            username=username,
            password=password,
        )

    def last_received_message(self):
        return self.__receiver.last_received_message

    def run(self) -> None:
        self.__receiver.run()

    def stop(self) -> None:
        self.__receiver.stop()
