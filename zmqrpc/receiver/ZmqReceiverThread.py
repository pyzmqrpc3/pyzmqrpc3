
from threading import Thread

from .ZmqReceiver import ZmqReceiver


class ZmqReceiverThread(Thread):
    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_sub_connect_addresses=None,
            recreate_sockets_on_timeout_of_sec=60,
            username=None,
            password=None):
        super().__init__()

        self.receiver = ZmqReceiver(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username=username,
            password=password,
        )

    def last_received_message(self):
        return self.receiver.last_received_message

    def run(self):
        self.receiver.run()

    def stop(self):
        self.receiver.stop()
