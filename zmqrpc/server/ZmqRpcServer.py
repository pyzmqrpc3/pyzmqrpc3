

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Dict, Optional, Tuple, Type

from ..command import ICommand, ShutdownServer, json_unzip
from ..receiver import SubSocketAddress, ZmqReceiver
from ..service import IService, ShutdownServerService


class ZmqRpcServer(ZmqReceiver):
    '''
    The ZmqRpcServer implements a ZmqReceiver and extends it with the ability
    to host one or more services that can be executed remotely by a
    ZmqRpcClient.
    In case a PUB/SUB connection is used, no response is provided.
    In case a REQ/REQ connection is used a response must be provided in
    order for the system to know the call was successful.
    The ZmqRpcServer constructor takes a collection of either REP or SUB
    addresses for the ZMQ layer.
    Multiple services and be registered with the server.
    Each service should be handeling a distinct command type.
    All commands inherit ICommand and all services inherit IService.
    Command types has to have a default constructor: i.e. it should be possible
    to construct the command object without any arguments.
    Out of the box, the server supports the command `ShutdownServer`.
    A username/password may be used for REQ/REP pairs (does not seem to be
    working for PUB/SUB sockets)
    '''

    def __init__(
            self,
            zmq_rep_bind_address: Optional[str] = None,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
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
        self.__services: Dict[str, IService] = {}

        self.register_service(
            command_class=ShutdownServer,
            service=ShutdownServerService(server=self),
        )

    def register_service(
            self,
            command_class: Type[ICommand],
            service: IService) -> None:
        if command_class is ICommand:
            raise RuntimeError('command_class cannot be ICommand')

        command_class_name = command_class.__name__

        if not issubclass(command_class, ICommand):
            raise RuntimeError(
                'command "%s" has to inherit ICommand' %
                command_class_name
            )

        try:
            command_class()
        except BaseException as e:
            raise RuntimeError(
                'command "%s" does not have a default constructor' %
                command_class_name
            ) from e

        if not isinstance(service, IService):
            raise RuntimeError(
                'service has to be an instance of concrete type that '
                'inherits IService'
            )

        if command_class_name in self.__services:
            raise RuntimeError(
                'found a repeated service "%s" for command "%s"' % (
                    type(service).__name__,
                    command_class_name,
                )
            )

        self.__services[command_class_name] = service

    def handle_incoming_message(self, message: str) -> Optional[str]:
        if message == self.HEARTBEAT_MSG:
            return None

        try:
            command: ICommand = json_unzip(message)
        except Exception as e:
            status_message = 'Incorrectly marshalled command. Incoming ' \
                'message is no proper json formatted string. ' \
                'Exception: {0}'.format(e)
            self._info(status_message)
            return self.create_response_message(
                status_code=self.STATUS_CODE_BAD_SERIALIZATION,
                status_message=status_message,
            )

        command_class_name = type(command).__name__

        service: Optional[IService] = self.__services.get(
            command_class_name,
            None,
        )

        if service is None:
            status_message = 'No service on the server is registered for' \
                ' command "%s".' % command_class_name
            self._warning(status_message)
            return self.create_response_message(
                status_code=self.STATUS_CODE_BAD_SERVICE,
                status_message=status_message,
            )

        self._debug('executing command: "%s"' % command_class_name)

        try:
            response_message = service(command)
        except Exception as e:
            status_message = 'Exception raised when calling service ' \
                '{0}. Exception: {1} '.format(type(service).__name__, e)
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
