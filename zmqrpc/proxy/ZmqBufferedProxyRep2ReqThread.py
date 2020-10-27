

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread

from .ZmqProxyRep2PubThread import ZmqProxyRep2PubThread
from .ZmqProxySub2ReqThread import ZmqProxySub2ReqThread


class ZmqBufferedProxyRep2ReqThread(Thread):
    '''
    This proxy class uses a 'hidden' pub/sub socket to buffer any messages
    from REP to REQ socket in case the REQ socket is offline.
    '''

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_req_connect_addresses=None,
            buffered_pub_address=None,
            buffered_sub_address=None,
            recreate_timeout=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        super().__init__()

        self.__proxy0 = ZmqProxyRep2PubThread(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_pub_bind_address=buffered_pub_address,
            recreate_timeout=100000,
            username_rep=username_rep,
            password_rep=password_rep,
        )

        self.__proxy1 = ZmqProxySub2ReqThread(
            zmq_sub_connect_addresses=[buffered_sub_address],
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_timeout=recreate_timeout,
            username_req=username_req,
            password_req=password_req,
        )

    def start(self) -> None:
        self.__proxy0.start()
        self.__proxy1.start()
        super().start()

    def stop(self) -> None:
        self.__proxy0.stop()
        self.__proxy1.stop()

    def join(self, timeout=None) -> None:
        self.__proxy0.join()
        self.__proxy1.join()
        super().join()
