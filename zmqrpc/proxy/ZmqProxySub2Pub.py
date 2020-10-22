
# This class implements a simple message forwarding from a PUB/SUB connection to another
# PUB/SUB connection. Could be used to aggregate messages into one end-point.
class ZmqProxySub2Pub(ZmqReceiver):
    # Note, at the moment username/password only protects the REQ-REP socket
    # connection
    def __init__(
            self,
            zmq_sub_connect_addresses,
            zmq_pub_bind_address,
            recreate_sockets_on_timeout_of_sec=600,
            username_sub=None,
            password_sub=None,
            username_pub=None,
            password_pub=None):
        ZmqReceiver.__init__(
            self,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username=username_sub,
            password=password_sub)
        self.sender = ZmqSender(
            zmq_pub_endpoint=zmq_pub_bind_address,
            username=username_pub,
            password=username_pub)

    def handle_incoming_message(self, message):
        # We don't care for the response, since we cannot pass it back via the
        # pub socket or we got none from a pub socket
        try:
            self.sender.send(message, time_out_waiting_for_response_in_sec=60)
        except Exception as e:
            logger.error(e)
        return None
