

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional

from .ZmqProxyRep2Pub import ZmqProxyRep2Pub
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxyRep2PubThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_rep_bind_address: str,
            zmq_pub_bind_address: str,
            recreate_timeout: Optional[int] = 600,
            proxy_timeout: Optional[int] = 60,
            username_rep: Optional[str] = None,
            password_rep: Optional[str] = None,
            username_pub: Optional[str] = None,
            password_pub: Optional[str] = None):
        super().__init__()

        self._set_proxy(
            proxy=ZmqProxyRep2Pub(
                zmq_rep_bind_address=zmq_rep_bind_address,
                zmq_pub_bind_address=zmq_pub_bind_address,
                recreate_timeout=recreate_timeout,
                proxy_timeout=proxy_timeout,
                username_rep=username_rep,
                password_rep=password_rep,
                username_pub=username_pub,
                password_pub=password_pub,
            )
        )
