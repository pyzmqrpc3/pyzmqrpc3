

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from ..receiver import SubSocketAddress
from .ZmqProxySub2Pub import ZmqProxySub2Pub
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxySub2PubThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...],
            zmq_pub_bind_address: str,
            recreate_timeout: Optional[int] = 600,
            proxy_timeout: Optional[int] = 60,
            username_sub: Optional[str] = None,
            password_sub: Optional[str] = None,
            username_pub: Optional[str] = None,
            password_pub: Optional[str] = None):
        super().__init__()

        self._set_proxy(
            proxy=ZmqProxySub2Pub(
                zmq_sub_connect_addresses=zmq_sub_connect_addresses,
                zmq_pub_bind_address=zmq_pub_bind_address,
                recreate_timeout=recreate_timeout,
                proxy_timeout=proxy_timeout,
                username_sub=username_sub,
                password_sub=password_sub,
                username_pub=username_pub,
                password_pub=password_pub,
            )
        )
