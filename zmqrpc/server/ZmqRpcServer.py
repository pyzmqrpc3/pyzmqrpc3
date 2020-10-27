

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
from typing import Callable, Dict, Optional, Tuple

from ..receiver import SubSocketAddress, ZmqReceiver


class ZmqRpcServer(ZmqReceiver):
    '''
    The ZmqRpcServer implements a ZmqReceiver and extends it with the ability
    to host one or more methods that can be invoked by a ZmqRpcClient.
    In case a PUB/SUB connection is used, no response is provided.
    In case a REQ/REQ connection is used a response must be provided in
    order for the system to know the call was successful.
    The ZmqRpcServer constructor takes a collection of either REP or SUB
    addresses for the ZMQ layer.
    The rpc_functions are dict structures mapping a string value to a
    real method implementation.
    A username/password may be used for REQ/REP pairs (does not seem to be
    working for PUB/SUB sockets
    '''

    def __init__(
            self,
            zmq_rep_bind_address: Optional[str] = None,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
            rpc_functions: Dict[str, Callable] = None,
            recreate_timeout: Optional[int] = 600,
            username: Optional[str] = None,
            password: Optional[str] = None):
        super().__init__(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            recreate_timeout=recreate_timeout,
            username=username,
            password=password,
        )
        self.__rpc_functions = rpc_functions or dict()

    def handle_incoming_message(self, message: str) -> Optional[str]:
        if message == self.HEARTBEAT_MSG:
            return None

        try:
            payload: dict = json.loads(message)
        except Exception as e:
            status_message = 'Incorrectly marshalled function. Incoming ' \
                'message is no proper json formatted string. ' \
                'Exception: {0}'.format(e)
            self._info(status_message)
            return self.create_response_message(
                status_code=self.STATUS_CODE_BAD_SERIALIZATION,
                status_message=status_message,
            )

        function_name = payload.get(self.RPC_FUNCTION, None)

        if function_name is None or function_name == '':
            status_message = 'Incorrectly marshalled function. ' \
                'No function name provided.'
            self._warning(status_message)
            return self.create_response_message(
                status_code=self.STATUS_CODE_MISSING_FUNCTION,
                status_message=status_message,
            )

        func_callback = self.__rpc_functions.get(function_name, None)

        if func_callback is None:
            status_message = 'Function "{0}" is not implemented on server. ' \
                'Check rpc_functions on server if it contains the ' \
                'function name'.format(function_name)
            self._warning(status_message)
            return self.create_response_message(
                status_code=self.STATUS_CODE_BAD_FUNCTION,
                status_message=status_message,
            )

        parameters = payload.get(self.RPC_PARAMETERS, [])

        try:
            response_message = func_callback(**parameters)
        except Exception as e:
            status_message = 'Exception raised when calling function ' \
                '{0}. Exception: {1} '.format(function_name, e)
            self._warning(status_message)
            self._exception(e)
            return self.create_response_message(
                status_code=self.STATUS_CODE_EXCEPTION_RAISED,
                status_message=status_message,
            )

        return self.create_response_message(
            status_code=self.STATUS_CODE_OK,
            status_message=self.STATUS_MSG_OK,
            response_message=response_message,
        )
