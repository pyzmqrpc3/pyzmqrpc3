

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .ZmqProxySub2Pub import ZmqProxySub2Pub
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxySub2PubThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_sub_connect_addresses=None,
            zmq_pub_bind_address=None,
            recreate_timeout=600,
            username_sub=None,
            password_sub=None,
            username_pub=None,
            password_pub=None):
        super().__init__()

        self.proxy = ZmqProxySub2Pub(
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            zmq_pub_bind_address=zmq_pub_bind_address,
            recreate_timeout=recreate_timeout,
            username_sub=username_sub,
            password_sub=password_sub,
            username_pub=username_pub,
            password_pub=password_pub,
        )
