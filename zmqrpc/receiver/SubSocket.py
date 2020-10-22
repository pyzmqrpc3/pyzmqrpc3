'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''

import logging
import time

import zmq
import zmq.auth

logger = logging.getLogger("zmqrpc")


class SubSocket:

    def __init__(self, ctx, poller, address, timeout_in_sec=None):
        self.ctx = ctx
        self.poller = poller
        self.address = address
        self.timeout_in_sec = timeout_in_sec
        self.zmq_socket = None
        self.create()

    def create(self):
        if not self.zmq_socket:
            self.zmq_socket = self.ctx.socket(zmq.SUB)
            self.zmq_socket.setsockopt(zmq.SUBSCRIBE, b'')
            self.zmq_socket.setsockopt(zmq.LINGER, 0)
            if isinstance(self.address, str):
                self.zmq_socket.connect(self.address)
            else:
                self.zmq_socket.connect(self.address[0])
                self.timeout_in_sec = self.address[1]
            self.poller.register(self.zmq_socket, zmq.POLLIN)
            self.last_received_bytes = time.time()
            logger.debug("Created SUB socket to %s", self.address)

    def destroy(self):
        if self.zmq_socket:
            self.poller.unregister(self.zmq_socket)
            address = self.address
            if isinstance(address, tuple):
                address = address[0]
            # Since some recent version of pyzmq it does not accept unbind
            # of an address with '*'. Replace it with 0.0.0.0
            if '*' in address:
                address = address.replace('*', '0.0.0.0')
            self.zmq_socket.disconnect(address)
            self.zmq_socket.close()
            while not self.zmq_socket.closed:
                time.sleep(1)
            self.zmq_socket = None
            logger.debug("Destroyed SUB socket bound to %s", self.address)

    def recv_string(self, socks):
        if self.zmq_socket is not None and (
                socks.get(self.zmq_socket) == zmq.POLLIN):
            result = self.zmq_socket.recv_string()
            self.last_received_bytes = time.time()
            return result
        if (self.timeout_in_sec is not None) and time.time(
        ) > self.last_received_bytes + self.timeout_in_sec:
            # Recreate sockets
            logger.warn(
                "Heartbeat timeout exceeded. Recreating SUB socket to %s",
                self.address)
            self.destroy()
            self.create()
        return None
