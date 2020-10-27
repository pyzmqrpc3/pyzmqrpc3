

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from .ZmqProxyRep2Req import ZmqProxyRep2Req
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxyRep2ReqThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_rep_bind_address: str,
            zmq_req_connect_addresses: Tuple[str, ...],
            recreate_timeout: Optional[int] = 600,
            proxy_timeout: Optional[int] = 60,
            username_rep: Optional[str] = None,
            password_rep: Optional[str] = None,
            username_req: Optional[str] = None,
            password_req: Optional[str] = None):
        super().__init__()

        self._set_proxy(
            proxy=ZmqProxyRep2Req(
                zmq_rep_bind_address=zmq_rep_bind_address,
                zmq_req_connect_addresses=zmq_req_connect_addresses,
                recreate_timeout=recreate_timeout,
                proxy_timeout=proxy_timeout,
                username_rep=username_rep,
                password_rep=password_rep,
                username_req=username_req,
                password_req=password_req,
            )
        )
