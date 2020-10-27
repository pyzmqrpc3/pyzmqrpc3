

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread
from typing import Callable, Dict, Optional, Tuple

from ..receiver import SubSocket, SubSocketAddress
from .ZmqRpcServer import ZmqRpcServer


class ZmqRpcServerThread(Thread):
    '''
    The same as a ZmqRpcServer implementation but implemented in a Thread
    environment.
    '''

    def __init__(
            self,
            zmq_rep_bind_address: Optional[str] = None,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
            rpc_functions: Dict[str, Callable] = None,
            recreate_timeout: Optional[int] = 60,
            username: Optional[str] = None,
            password: Optional[str] = None):
        super().__init__()

        self.__server = ZmqRpcServer(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            rpc_functions=rpc_functions,
            recreate_timeout=recreate_timeout,
            username=username,
            password=password,
        )

    def get_last_received_message(self) -> Optional[str]:
        return self.__server.get_last_received_message()

    def run(self) -> None:
        self.__server.run()

    def stop(self) -> None:
        self.__server.stop()

    def get_sub_socket(self, idx: int) -> SubSocket:
        return self.__server.get_sub_socket(idx=idx)
