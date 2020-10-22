

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .ZmqProxyRep2Pub import ZmqProxyRep2Pub
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxyRep2PubThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_pub_bind_address=None,
            recreate_timeout=600,
            username_rep=None,
            password_rep=None,
            username_pub=None,
            password_pub=None):
        super().__init__()

        self.proxy = ZmqProxyRep2Pub(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_pub_bind_address=zmq_pub_bind_address,
            recreate_timeout=recreate_timeout,
            username_rep=username_rep,
            password_rep=password_rep,
            username_pub=username_pub,
            password_pub=password_pub,
        )
