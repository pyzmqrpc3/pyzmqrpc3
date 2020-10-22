

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from ..logger import logger
from ..receiver import ZmqReceiver
from ..sender import ZmqSender


class ZmqProxySub2Req(ZmqReceiver):
    '''
    # This class implements a simple message forwarding from a PUB/SUB
    # connection to a REQ/REP connection.
    # Note, at the moment username/password only protects the REQ-REP socket
    # connection
    '''

    def __init__(
            self,
            zmq_sub_connect_addresses,
            zmq_req_connect_addresses,
            recreate_timeout=600,
            username_sub=None,
            password_sub=None,
            username_req=None,
            password_req=None):
        super().__init__(
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_timeout=recreate_timeout,
            username=username_sub,
            password=password_sub,
        )

        self.sender = ZmqSender(
            zmq_req_endpoints=zmq_req_connect_addresses,
            username=username_req,
            password=password_req,
        )

    def handle_incoming_message(self, message):
        # We don't care for the response, since we cannot pass it back via the
        # pub socket or we got none from a pub socket
        try:
            self.sender.send(message, time_out_in_sec=60)
        except Exception as e:
            logger.error(e)
        return None
