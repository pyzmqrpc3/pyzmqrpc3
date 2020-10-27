

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional

from .ZmqProxy import ZmqProxy


class ZmqProxyRep2Pub(ZmqProxy):
    '''
    This class implements a simple message forwarding from a REQ/REP
    connection to a PUB/SUB connection.
    Note, at the moment username/password only protects the REQ-REP socket
    connection
    '''

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
        super().__init__(
            recv_rep_bind_address=zmq_rep_bind_address,
            recv_recreate_timeout=recreate_timeout,
            recv_username=username_rep,
            recv_password=password_rep,
            proxy_timeout=proxy_timeout,
            send_pub_endpoint=zmq_pub_bind_address,
            send_username=username_pub,
            send_password=password_pub,
        )
