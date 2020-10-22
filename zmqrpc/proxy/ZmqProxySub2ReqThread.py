

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .ZmqProxySub2Req import ZmqProxySub2Req
from .ZmqProxyThread import ZmqProxyThread


class ZmqProxySub2ReqThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_sub_connect_addresses=None,
            zmq_req_connect_addresses=None,
            recreate_timeout=600,
            username_sub=None,
            password_sub=None,
            username_req=None,
            password_req=None):
        super().__init__()

        self.proxy = ZmqProxySub2Req(
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_timeout=recreate_timeout,
            username_sub=username_sub,
            password_sub=password_sub,
            username_req=username_req,
            password_req=password_req,
        )
