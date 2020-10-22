
class ZmqProxySub2ReqThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_sub_connect_addresses=None,
            zmq_req_connect_addresses=None,
            recreate_sockets_on_timeout_of_sec=600,
            username_sub=None,
            password_sub=None,
            username_req=None,
            password_req=None):
        ZmqProxyThread.__init__(self)
        self.proxy = ZmqProxySub2Req(
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username_sub=username_sub,
            password_sub=password_sub,
            username_req=username_req,
            password_req=password_req)
