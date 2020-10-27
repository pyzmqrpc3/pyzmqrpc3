

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread
from typing import Optional, Tuple

from .SubSocket import SubSocket, SubSocketAddress
from .ZmqReceiver import ZmqReceiver


class ZmqReceiverThread(Thread):

    def __init__(
            self,
            zmq_rep_bind_address: Optional[str] = None,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
            recreate_timeout: int = 60,
            username: Optional[str] = None,
            password: Optional[str] = None):
        super().__init__()

        self.__receiver = ZmqReceiver(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_timeout=recreate_timeout,
            username=username,
            password=password,
        )

    def stop(self) -> None:
        self.__receiver.stop()

    def run(self) -> None:
        self.__receiver.run()

    def get_last_received_message(self) -> Optional[str]:
        return self.__receiver.get_last_received_message()

    def get_sub_socket(self, idx: int) -> SubSocket:
        return self.__receiver.get_sub_socket(idx=idx)
