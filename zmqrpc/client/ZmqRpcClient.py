

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional, Tuple

from ..command import ICommand, json_zip
from ..sender import ZmqSender


class ZmqRpcClient(ZmqSender):
    '''
    The ZmqRpcClient class implements a ZmqSender class but extends it with the
    ability to execute a command on a remote server. Command execution is
    implemented by providing a concrete instance of the ICommand type.
    The constructor of the class requires the ZMQ endpoints to be provided
    as well as (optionally) a username/password to 'secure' the connection.
    '''

    def execute_remote(
            self,
            command: ICommand,
            time_out_in_sec: Optional[int] = 600) \
            -> Optional[Tuple[object, ...]]:
        '''
        Execute a command on a remote ZeroMQ process and returns the result
        of calling the service in case of a REQ socket.
        time_out_in_sec indicates the time to wait for a response of
        the server. If none is received in the given time
        the system does not try again and will discard the message, never
        knowing if it was received by the server or not.
        '''

        command_class_name = type(command).__name__

        self._debug('sending command: "%s', command_class_name)

        # Try to serialize. If it fails, throw an error and exit.
        try:
            message = json_zip(command)
        except Exception as e:
            raise RuntimeError(
                'Cannot wrap parameters in json format.'
            ) from e

        ret = self.send(
            message=message,
            time_out_in_sec=time_out_in_sec,
        )

        self._debug('execution result received')

        return ret
