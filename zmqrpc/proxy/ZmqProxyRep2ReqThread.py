
class ZmqProxyRep2ReqThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_req_connect_addresses=None,
            recreate_sockets_on_timeout_of_sec=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        ZmqProxyThread.__init__(self)
        self.proxy = ZmqProxyRep2Req(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_req_connect_addresses=zmq_req_connect_addresses,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username_rep=username_rep,
            password_rep=password_rep,
            username_req=username_req,
            password_req=password_req)
