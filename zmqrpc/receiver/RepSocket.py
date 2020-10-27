

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import time
from typing import Optional

import zmq
from zmq.auth.thread import ThreadAuthenticator

from ..logger import logger


class RepSocket:

    def __init__(
            self,
            ctx: zmq.Context,
            poller: zmq.Poller,
            address: str,
            auth: Optional[ThreadAuthenticator]):
        self.__ctx = ctx
        self.__poller = poller
        self.__address = address
        self.__auth = auth
        self.__zmq_socket = None

        self.create()

    def create(self) -> None:
        if self.__zmq_socket is not None:
            return

        self.__zmq_socket = zmq_socket = self.__ctx.socket(zmq.REP)

        zmq_socket.setsockopt(zmq.LINGER, 0)

        if self.__auth:
            zmq_socket.plain_server = True

        zmq_socket.bind(self.__address)

        self.__poller.register(zmq_socket, zmq.POLLIN)

        logger.debug('Created REP socket bound to "%s"', self.__address)

    def destroy(self) -> None:
        if self.__zmq_socket is None:
            return

        self.__poller.unregister(self.__zmq_socket)

        address = self.__address
        # Since some recent version of pyzmq it does not accept unbind
        # of an address with '*'. Replace it with 0.0.0.0
        if '*' in address:
            address = address.replace('*', '0.0.0.0')

        self.__zmq_socket.unbind(address)
        self.__zmq_socket.close()

        while not self.__zmq_socket.closed:
            time.sleep(1)

        self.__zmq_socket = None

        logger.debug('Destroyed REP socket bound to "%s"', self.__address)

    def recv_string(self, socks: dict) -> Optional[str]:
        if self.__zmq_socket is not None and (
                socks.get(self.__zmq_socket) == zmq.POLLIN):
            return self.__zmq_socket.recv_string()
        return None

    def send(self, message: str) -> None:
        if self.__zmq_socket is None or message is None:
            return

        self.__zmq_socket.send_string(message)
