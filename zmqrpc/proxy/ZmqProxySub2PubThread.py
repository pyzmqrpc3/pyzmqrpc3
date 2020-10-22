

class ZmqProxySub2PubThread(ZmqProxyThread):
    def __init__(
            self,
            zmq_sub_connect_addresses=None,
            zmq_pub_bind_address=None,
            recreate_sockets_on_timeout_of_sec=600,
            username_sub=None,
            password_sub=None,
            username_pub=None,
            password_pub=None):
        ZmqProxyThread.__init__(self)
        self.proxy = ZmqProxySub2Pub(
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            zmq_pub_bind_address=zmq_pub_bind_address,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username_sub=username_sub,
            password_sub=password_sub,
            username_pub=username_pub,
            password_pub=password_pub)
