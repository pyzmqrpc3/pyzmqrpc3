

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from ..receiver import SubSocketAddress
from .ZmqProxy import ZmqProxy


class ZmqProxySub2Req(ZmqProxy):
    '''
    # This class implements a simple message forwarding from a PUB/SUB
    # connection to a REQ/REP connection.
    # Note, at the moment username/password only protects the REQ-REP socket
    # connection
    '''

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
        super().__init__(
            recv_sub_connect_addresses=zmq_sub_connect_addresses,
            recv_recreate_timeout=recreate_timeout,
            recv_username=username_sub,
            recv_password=password_sub,
            proxy_timeout=proxy_timeout,
            send_req_endpoints=zmq_req_connect_addresses,
            send_username=username_req,
            send_password=password_req,
        )
