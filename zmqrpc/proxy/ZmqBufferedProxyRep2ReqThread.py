'''
Created on Apr 8, 2014

@author: Jan Verhoeven

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''
from __future__ import print_function

import logging
from builtins import super
from threading import Thread

from .ZmqReceiver import ZmqReceiver
from .ZmqSender import ZmqSender

logger = logging.getLogger("zmqrpc")


# This proxy class uses a 'hidden' pub/sub socket to buffer any messages from REP to REQ socket
# in case the REQ socket is offline.
class ZmqBufferedProxyRep2ReqThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_req_connect_addresses=None,
            buffered_pub_address="tcp://*:59878",
            buffered_sub_address="tcp://localhost:59878",
            recreate_sockets_on_timeout_of_sec=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        ZmqProxyThread.__init__(self)
        self.proxy1 = ZmqProxyRep2PubThread(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_pub_bind_address=buffered_pub_address,
            recreate_sockets_on_timeout_of_sec=100000,
            username_rep=username_rep,
            password_rep=password_rep)
        self.proxy2 = ZmqProxySub2ReqThread(
            zmq_sub_connect_addresses=[buffered_sub_address],
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username_req=username_req,
            password_req=password_req)

    def start(self):
        self.proxy1.start()
        self.proxy2.start()
        super().start()

    def stop(self):
        self.proxy1.stop()
        self.proxy2.stop()

    def join(self, timeout=None):
        self.proxy1.join()
        self.proxy2.join()
        super().join()
