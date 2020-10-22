

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .ZmqProxyRep2Req import ZmqProxyRep2Req
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxyRep2ReqThread(ZmqProxyThread):

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_req_connect_addresses=None,
            recreate_timeout=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        super().__init__()

        self.proxy = ZmqProxyRep2Req(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_timeout=recreate_timeout,
            username_rep=username_rep,
            password_rep=password_rep,
            username_req=username_req,
            password_req=password_req,
        )
