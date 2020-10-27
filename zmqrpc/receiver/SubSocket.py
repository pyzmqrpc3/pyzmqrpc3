

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import time
from typing import Optional, Tuple, Union

import zmq
import zmq.auth

from ..logger import logger

SubSocketAddress = Union[str, Tuple[str, int]]


class SubSocket:

    def __init__(
            self,
            ctx: zmq.Context,
            poller: zmq.Poller,
            address: SubSocketAddress,
            timeout_in_sec: Optional[int] = None):
        self.__ctx = ctx
        self.__poller = poller
        self.__address: str = None
        self.__timeout_in_sec: Optional[int] = timeout_in_sec
        self.__zmq_socket: Optional[zmq.Socket] = None
        self.__last_received_time = None

        if isinstance(address, str):
            self.__address = str(address)
        else:
            address_list: Tuple[str, int] = tuple(address)
            self.__address = address_list[0]
            self.__timeout_in_sec: int = address_list[1]

        self.create()

    @property
    def has_zmq_socket(self) -> bool:
        return self.__zmq_socket is not None

    @property
    def zmq_socket(self) -> Optional[zmq.Socket]:
        return self.__zmq_socket

    def create(self) -> None:
        if self.has_zmq_socket:
            return

        self.__zmq_socket = zmq_socket = self.__ctx.socket(zmq.SUB)

        zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
        zmq_socket.setsockopt(zmq.LINGER, 0)

        zmq_socket.connect(self.__address)

        self.__poller.register(zmq_socket, zmq.POLLIN)
        self.__last_received_time = time.time()
        logger.debug('Created SubSocket to "%s"', self.__address)

    def destroy(self) -> None:
        if not self.has_zmq_socket:
            return

        zmq_socket = self.zmq_socket

        self.__poller.unregister(zmq_socket)

        address = self.__address
        if isinstance(address, tuple):
            address = address[0]
        # Since some recent version of pyzmq it does not accept unbind
        # of an address with '*'. Replace it with 0.0.0.0
        if '*' in address:
            address = address.replace('*', '0.0.0.0')

        zmq_socket.disconnect(address)
        zmq_socket.close()

        while not zmq_socket.closed:
            time.sleep(1)

        self.__zmq_socket = None

        logger.debug('Destroyed SubSocket bound to "%s"', self.__address)

    def recv_string(self, socks: dict) -> Optional[str]:
        if self.has_zmq_socket and (socks.get(self.zmq_socket) == zmq.POLLIN):
            result = self.zmq_socket.recv_string()
            self.__last_received_time = time.time()
            return result

        if (self.__timeout_in_sec is not None) and time.time(
        ) > self.__last_received_time + self.__timeout_in_sec:
            # Recreate sockets
            logger.warning(
                'Heartbeat timeout exceeded. Recreating SubSocket to "%s"',
                self.__address
            )
            self.destroy()
            self.create()

        return None
