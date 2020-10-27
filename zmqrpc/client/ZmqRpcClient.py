

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
from typing import Optional, Tuple

from ..sender import ZmqSender


class ZmqRpcClient(ZmqSender):
    '''
    The ZmqRpcClient class implements a ZmqSender class but extends it with the
    ability to invoke a method on a remote server. Method invocation is
    implemented by providing a function name to invoke (function_name) and
    the function_parameters as a dict. The constructor of the class requires
    the ZMQ endpoints to be provided as well as (optionally) a
    username/password to 'secure' the connection.
    '''

    def invoke(
            self,
            function_name: str,
            function_parameters: Tuple[object] = None,
            time_out_in_sec: Optional[int] = 600) -> Tuple[object]:
        '''
        Invokes a function on a remote ZeroMQ process and returns the result
        of calling the function in case of a REQ socket. Parameters should
        be a dict.
        time_out_in_sec indicates the time to wait
        for a response of the server. If none is received in the given time
        the system does not try again and will discard the message, never
        knowing if it was received by the server or not.
        '''

        # Try to serialize. If it fails, throw an error and exit.
        payload = {
            self.RPC_FUNCTION: function_name,
        }

        if function_parameters is not None:
            payload[self.RPC_PARAMETERS] = function_parameters

        try:
            message = json.dumps(payload)
        except Exception as e:
            raise RuntimeError(
                'Cannot wrap parameters in json format. '
            ) from e

        return self.send(
            message=message,
            time_out_in_sec=time_out_in_sec,
        )
