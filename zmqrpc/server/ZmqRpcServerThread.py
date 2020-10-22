
# The same as a ZmqRpcServer implementation but implemented in a Thread
# environment.
class ZmqRpcServerThread(Thread):
    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_sub_connect_addresses=None,
            rpc_functions=None,
            recreate_sockets_on_timeout_of_sec=60,
            username=None,
            password=None):
        Thread.__init__(self)
        self.server = ZmqRpcServer(
            zmq_rep_bind_address,
            zmq_sub_connect_addresses,
            rpc_functions,
            recreate_sockets_on_timeout_of_sec,
            username,
            password)

    def last_received_message(self):
        return self.server.last_received_message

    def run(self):
        self.server.run()

    def stop(self):
        self.server.stop()
