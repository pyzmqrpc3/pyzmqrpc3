

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
            recreate_timeout=600,
            username_rep=None,
            password_rep=None,
            username_req=None,
            password_req=None):
        super().__init__(
            zmq_rep_bind_address=zmq_rep_bind_address,
            recreate_timeout=recreate_timeout,
            username=username_rep,
            password=password_rep,
        )

        self.__sender = ZmqSender(
            zmq_req_endpoints=zmq_req_connect_addresses,
            username=username_req,
            password=password_req,
        )

    def handle_incoming_message(self, message):
        # Pass on the response from the forwarding socket.
        try:
            self.__sender.send(
                message, time_out_in_sec=60)
            return self.create_response_message(
                status_code=200,
                status_message="OK",
            )
        except Exception as e:
            return self.create_response_message(
                status_code=400,
                status_message='Error',
                response_message=e,
            )
