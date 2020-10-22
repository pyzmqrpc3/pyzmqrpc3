
# This class implements a simple message forwarding from a REQ/REP connection to a
# PUB/SUB connection.
class ZmqProxyRep2Pub(ZmqReceiver):
    # Note, at the moment username/password only protects the REQ-REP socket
    # connection
    def __init__(
            self,
            zmq_rep_bind_address,
            zmq_pub_bind_address,
            recreate_sockets_on_timeout_of_sec=600,
            username_rep=None,
            password_rep=None,
            username_pub=None,
            password_pub=None):
        ZmqReceiver.__init__(
            self,
            zmq_rep_bind_address=zmq_rep_bind_address,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username=username_rep,
            password=password_rep)
        self.sender = ZmqSender(
            zmq_req_endpoints=None,
            zmq_pub_endpoint=zmq_pub_bind_address,
            username=username_pub,
            password=password_pub)

    def handle_incoming_message(self, message):
        try:
            self.sender.send(message, time_out_waiting_for_response_in_sec=60)
            # Pub socket does not provide response message, so return OK message
            return self.create_response_message(200, "OK", None)
        except Exception as e:
            return self.create_response_message(
                status_code=400, status_message="Error", response_message=e)
