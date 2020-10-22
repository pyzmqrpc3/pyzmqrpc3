

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import time

import zmq
import zmq.auth

from ..logger import logger


class RepSocket:

    def __init__(self, ctx, poller, address, auth):
        self.ctx = ctx
        self.poller = poller
        self.address = address
        self.auth = auth
        self.zmq_socket = None
        self.create()

    def create(self):
        if not self.zmq_socket:
            self.zmq_socket = self.ctx.socket(zmq.REP)
            self.zmq_socket.setsockopt(zmq.LINGER, 0)
            if self.auth:
                self.zmq_socket.plain_server = True
            self.zmq_socket.bind(self.address)
            self.poller.register(self.zmq_socket, zmq.POLLIN)
            logger.debug("Created REP socket bound to %s", self.address)

    def destroy(self):
        if self.zmq_socket:
            self.poller.unregister(self.zmq_socket)
            address = self.address
            # Since some recent version of pyzmq it does not accept unbind
            # of an address with '*'. Replace it with 0.0.0.0
            if '*' in address:
                address = address.replace('*', '0.0.0.0')
            self.zmq_socket.unbind(address)
            self.zmq_socket.close()
            while not self.zmq_socket.closed:
                time.sleep(1)
            self.zmq_socket = None
            logger.debug("Destroyed REP socket bound to %s", self.address)

    def recv_string(self, socks):
        if self.zmq_socket is not None and (
                socks.get(self.zmq_socket) == zmq.POLLIN):
            result = self.zmq_socket.recv_string()
            self.last_received_bytes = time.time()
            return result
        return None

    def send(self, message):
        if self.zmq_socket is not None and message is not None:
            self.zmq_socket.send_string(message)
