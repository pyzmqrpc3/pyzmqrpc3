

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from ..receiver import SubSocketAddress, ZmqReceiver
from ..sender import ZmqSender


class ZmqProxy(ZmqReceiver):

    def __init__(
            self,
            recv_rep_bind_address: Optional[str] = None,
            recv_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
            recv_recreate_timeout: Optional[int] = 600,
            recv_username: Optional[str] = None,
            recv_password: Optional[str] = None,
            proxy_timeout: Optional[int] = 60,
            send_req_endpoints: Tuple[str, ...] = None,
            send_pub_endpoint: Optional[str] = None,
            send_username: Optional[str] = None,
            send_password: Optional[str] = None):
        super().__init__(
            zmq_rep_bind_address=recv_rep_bind_address,
            zmq_sub_connect_addresses=recv_sub_connect_addresses,
            recreate_timeout=recv_recreate_timeout,
            username=recv_username,
            password=recv_password,
        )

        self.__proxy_timeout = proxy_timeout
        self.__sender = ZmqSender(
            zmq_req_endpoints=send_req_endpoints,
            zmq_pub_endpoint=send_pub_endpoint,
            username=send_username,
            password=send_password,
        )

    def handle_incoming_message(self, message: str) -> Optional[str]:
        try:
            self._debug('marshaling proxy message')
            self.__sender.send(
                message=message,
                time_out_in_sec=self.__proxy_timeout,
            )
            return self.create_response_message(
                status_code=self.STATUS_CODE_OK,
                status_message=self.STATUS_MSG_OK,
            )
        except Exception as e:
            self._error(e)
            return self.create_response_message(
                status_code=self.STATUS_CODE_PROXY_ERROR,
                status_message='Error',
                response_message=e,
            )
