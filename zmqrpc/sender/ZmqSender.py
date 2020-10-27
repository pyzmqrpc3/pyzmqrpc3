

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
import time
from typing import Optional, Tuple

import zmq

from ..base import ZmqBase


class ZmqSender(ZmqBase):
    '''
    ZmqSender implements a ZeroMQ REQ or PUB socket to send messages out via a
    send function. The send function is equipped with a timeout and automatic
    recreation of the underlying REQ socket if no message is received back
    in the given timeout.
    The username/password can be used to provide 'simple' protection on
    the wire (only PLAIN has been implemented, so be aware of sniffers).
    '''

    def __init__(
            self,
            zmq_req_endpoints: Tuple[str, ...] = None,
            zmq_pub_endpoint: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None):
        self.__context = zmq.Context()
        self.__poller = zmq.Poller()

        self.__username = username
        self.__password = password

        self.__zmq_req_endpoints: Tuple[str, ...] = tuple(
            zmq_req_endpoints or []
        )
        self.__zmq_pub_endpoint = zmq_pub_endpoint

        self.__pub_socket: zmq.Socket = None
        self.__req_sockets: Tuple[zmq.Socket, ...] = None

        self.__recreate_pub_socket = False
        self.__recreate_req_socket = False

        self.create_pub_socket()
        self.create_req_socket()

    @property
    def has_username_and_password(self) -> bool:
        return self.__username and self.__password

    def create_pub_socket(self) -> None:
        if self.__pub_socket is not None:
            raise RuntimeError(
                'Want create new PUB socket, but old PUB Socket is not '
                'destroyed.'
            )

        pub_endpoint = self.__zmq_pub_endpoint

        if pub_endpoint is None:
            return

        self.__pub_socket = socket = self.__context.socket(zmq.PUB)
        if self.has_username_and_password:
            socket.plain_username = self.__username
            socket.plain_password = self.__password

        # Make sure we buffer enough (100000 messages) in case of network
        # troubles...
        socket.setsockopt(zmq.SNDHWM, 100000)

        try:
            self._debug('Bind PUB socket to "%s"', pub_endpoint)
            socket.bind(pub_endpoint)
        except Exception as e:
            raise Exception(
                'Cannot bind PUB socket to "{0}"'.format(pub_endpoint)
            ) from e

    def destroy_pub_socket(self) -> None:
        if self.__pub_socket is None:
            return

        socket = self.__pub_socket
        end_point = self.__zmq_pub_endpoint

        # Since some recent version of pyzmq it does not accept unbind
        # of an address with '*'. Replace it with 0.0.0.0
        end_point = end_point.replace('*', '0.0.0.0')

        error_message = ''

        try:
            socket.setsockopt(zmq.LINGER, 0)
        except Exception as e:
            error_message += 'Cannot set LINGER socket option. ' \
                'Exception: {0}\n'.format(e)

        self._debug('Unbind PUB socket to "%s"', end_point)
        try:
            socket.unbind(end_point)
        except Exception as e:
            raise Exception(
                'Cannot unbind PUB socket from {0}.'.format(end_point)
            ) from e

        self._debug('Close PUB socket to "%s"', end_point)
        try:
            socket.close()
        except Exception as e:
            error_message += 'Cannot close PUB socket. ' \
                'Exception: {0}\n'.format(e)

        self.__pub_socket = None
        if error_message:
            self._error(error_message)

    def create_req_socket(self) -> None:
        if self.__req_sockets is not None:
            raise RuntimeError(
                'Want create new REQ socket, but old REQ Socket is '
                'not destroyed.')

        if not self.__zmq_req_endpoints:
            return

        socket_list = []

        for end_point in self.__zmq_req_endpoints:
            socket = self.__context.socket(zmq.REQ)

            if self.has_username_and_password:
                socket.setsockopt_string(
                    zmq.PLAIN_USERNAME,
                    self.__username,
                )

                socket.setsockopt_string(
                    zmq.PLAIN_PASSWORD,
                    self.__password,
                )

            self._debug('Connect REQ socket to "%s"', end_point)

            try:
                socket.connect(end_point)
            except Exception as e:
                raise Exception(
                    'Cannot connect REQ socket to {0}.'.format(end_point)
                ) from e

            try:
                self.__poller.register(socket, zmq.POLLIN)
            except Exception as e:
                raise Exception('Cannot register REQ socket to poller.') from e

            socket_list.append(socket)

        self.__req_sockets = tuple(socket_list)

    def destroy_req_socket(self) -> None:
        if self.__req_sockets is None:
            return

        error_message = ''

        for end_point, socket in zip(
                self.__zmq_req_endpoints, self.__req_sockets):

            try:
                self.__poller.unregister(socket)
            except Exception as e:
                error_message += 'Cannot un-register REQ socket to poller. ' \
                    'Exception: {0}\n'.format(e)

            try:
                socket.setsockopt(zmq.LINGER, 0)
            except Exception as e:
                error_message += 'Cannot set LINGER socket option. ' \
                    'Exception: {0}\n'.format(e)

            self._debug('Disconnect REQ socket to "%s"', end_point)
            try:
                socket.disconnect(end_point)
            except Exception as e:
                error_message += 'Cannot disconnect REQ socket. ' \
                    'Exception: {0}\n'.format(e)

            self._debug('Close REQ socket to "%s"', self.__zmq_req_endpoints)
            try:
                socket.close()
            except Exception as e:
                error_message += 'Cannot close REQ socket. ' \
                    'Exception: {0}\n'.format(e)

        self.__req_sockets = None
        if error_message:
            self._error(error_message)

    def _send_over_pub_socket(self, message: str) -> None:
        if self.__pub_socket is None:
            return

        try:
            self.__pub_socket.send_string(message)
        except Exception as e:
            self.__recreate_pub_socket = True
            raise RuntimeError(
                'Cannot send message on PUB socket. Highly exceptional. '
                'Mark PUB socket for renewal. Consider this message lost.'
            ) from e

    def _handle_response(self, message: str) -> Tuple[bool, object]:
        try:
            payload: dict = json.loads(message)
        except BaseException as e:
            self.__recreate_req_socket = True
            return (
                False,
                Exception(
                    'Marshalling error: Response is not a json message. '
                    'Exception {0}'.format(e)
                ),
            )

        status_code: int = payload.get(self.STATUS_CODE, None)

        if status_code is None:
            self.__recreate_req_socket = True
            return (
                False,
                Exception('No status_code in response.'),
            )

        status_message = payload.get(self.STATUS_MSG, None)

        if status_code != self.STATUS_CODE_OK:
            self.__recreate_req_socket = True
            return (
                False,
                Exception(
                    status_message
                    if status_message else
                    'Error occurred with code {0}'.format(status_code)
                ),
            )

        return (
            True,
            payload.get(self.RESPONSE_MSG, None),
        )

    def _send_over_req_socket(
            self,
            message: str,
            time_out_in_sec: int = 10) -> Tuple[object]:
        if self.__req_sockets is None:
            return None

        response_list = [None] * len(self.__zmq_req_endpoints)

        for idx, (end_point, socket) in enumerate(zip(
                self.__zmq_req_endpoints, self.__req_sockets)):
            try:
                socket.send_string(message)
            except Exception as e:
                self.__recreate_req_socket = True
                response_list[idx] = (
                    False, Exception(
                        'Cannot send message on REQ socket {0}. This is very '
                        'exceptional. Please check logs. Marking REQ socket '
                        'to be recreated on next try. Message can be considered '
                        'lost. Exception {1}'.format(
                            end_point, e,), ))

        # Wait for given time to receive response.
        expire_time = time.time() + time_out_in_sec
        while expire_time > time.time():
            for idx, (end_point, socket) in enumerate(zip(
                    self.__zmq_req_endpoints, self.__req_sockets)):
                if response_list[idx] is not None:
                    continue

                # X seconds timeout before quiting on waiting for response
                req_socks = dict(self.__poller.poll(1000))
                if req_socks.get(socket) != zmq.POLLIN:
                    continue

                try:
                    response_message = socket.recv_string()
                except Exception as e:
                    self.__recreate_req_socket = True
                    response_list[idx] = (
                        False,
                        Exception(
                            'Could not receive message from socket %s. '
                            'Marking REQ socket to be recreated on next '
                            'try. Exception: %s'.format(end_point, e)
                        ),
                    )
                    continue

                response_list[idx] = self._handle_response(response_message)

            if all(response_list):
                break

        # Some unexpected socket related error occurred. Recreate the
        # REQ socket.
        if not all(response_list):
            self.__recreate_req_socket = True
            raise Exception(
                'No response received on ZMQ Request to end point'
                ' {0} in {1} seconds. Discarding message. Marking REQ '
                'socket to be recreated on next try.'.format(
                    self.__zmq_req_endpoints,
                    time_out_in_sec,
                )
            )

        if self.__recreate_req_socket:
            for response in response_list:
                if not response or not isinstance(response[1], BaseException):
                    continue
                raise response[1]

        return tuple(
            response[1] if response else None
            for response in response_list
        )

    def send(
            self,
            message: str,
            time_out_in_sec: int = 60) -> Tuple[object]:
        # Create sockets if needed. Raise an exception if any problems are
        # encountered
        if self.__recreate_pub_socket:
            self.destroy_pub_socket()
            self.create_pub_socket()
            self.__recreate_pub_socket = False

        if self.__recreate_req_socket:
            self.destroy_req_socket()
            self.create_req_socket()
            self.__recreate_req_socket = False

        # Sockets must exist otherwise we would not be here...
        # Any errors in the following lines will throw an error that must be
        # caught
        self._send_over_pub_socket(message)
        return self._send_over_req_socket(
            message,
            time_out_in_sec,
        )

    def send_heartbeat(self) -> None:
        self.send(self.HEARTBEAT_MSG)

    def destroy(self) -> None:
        self.destroy_req_socket()
        self.destroy_pub_socket()
