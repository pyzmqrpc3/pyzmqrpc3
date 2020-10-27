

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from ..receiver import SubSocketAddress
from .ZmqProxySub2Req import ZmqProxySub2Req
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxySub2ReqThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...],
            zmq_req_connect_addresses: Tuple[str, ...],
            recreate_timeout: Optional[int] = 600,
            proxy_timeout: Optional[int] = 60,
            username_sub: Optional[str] = None,
            password_sub: Optional[str] = None,
            username_req: Optional[str] = None,
            password_req: Optional[str] = None):
        super().__init__()

        self._set_proxy(
            proxy=ZmqProxySub2Req(
                zmq_sub_connect_addresses=zmq_sub_connect_addresses,
                zmq_req_connect_addresses=zmq_req_connect_addresses,
                recreate_timeout=recreate_timeout,
                proxy_timeout=proxy_timeout,
                username_sub=username_sub,
                password_sub=password_sub,
                username_req=username_req,
                password_req=password_req,
            )
        )
