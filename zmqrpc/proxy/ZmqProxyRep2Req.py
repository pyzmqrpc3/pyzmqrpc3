

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from ..receiver import ZmqReceiver
from ..sender import ZmqSender


class ZmqProxyRep2Req(ZmqReceiver):
    '''
    This class implements a simple message forwarding from a REQ/REP
    connection to another REQ/REP connection.
    Note, at the moment username/password only protects the REQ-REP socket
    connection
    '''

    def __init__(
            self,
            zmq_rep_bind_address,
            zmq_req_connect_addresses,
            recreate_sockets_on_timeout_of_sec=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        super().__init__(
            zmq_rep_bind_address=zmq_rep_bind_address,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username=username_rep,
            password=password_rep,
        )

        self.sender = ZmqSender(
            zmq_req_endpoints=zmq_req_connect_addresses,
            username=username_req,
            password=password_req)

    def handle_incoming_message(self, message):
        # Pass on the response from the forwarding socket.
        try:
            response_message = self.sender.send(
                message, time_out_waiting_for_response_in_sec=60)
            return self.create_response_message(
                status_code=200,
                status_message="OK",
                response_message=response_message)
        except Exception as e:
            return self.create_response_message(
                status_code=400, status_message="Error", response_message=e)
