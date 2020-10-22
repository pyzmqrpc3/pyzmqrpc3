

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from ..receiver import ZmqReceiver
from ..sender import ZmqSender


class ZmqProxyRep2Pub(ZmqReceiver):
    '''
    This class implements a simple message forwarding from a REQ/REP
    connection to a PUB/SUB connection.
    Note, at the moment username/password only protects the REQ-REP socket
    connection
    '''

    def __init__(
            self,
            zmq_rep_bind_address,
            zmq_pub_bind_address,
            recreate_timeout=600,
            username_rep=None,
            password_rep=None,
            username_pub=None,
            password_pub=None):
        super().__init__(
            zmq_rep_bind_address=zmq_rep_bind_address,
            recreate_timeout=recreate_timeout,
            username=username_rep,
            password=password_rep,
        )

        self.__sender = ZmqSender(
            zmq_req_endpoints=None,
            zmq_pub_endpoint=zmq_pub_bind_address,
            username=username_pub,
            password=password_pub,
        )

    def handle_incoming_message(self, message):
        try:
            self.__sender.send(message, time_out_in_sec=60)
            # Pub socket does not provide response message, so return OK message
            return self.create_response_message(200, "OK")
        except Exception as e:
            return self.create_response_message(
                status_code=400,
                status_message="Error",
                response_message=e,
            )
