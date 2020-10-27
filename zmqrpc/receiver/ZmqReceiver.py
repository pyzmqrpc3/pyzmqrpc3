

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
from typing import Optional, Tuple

import zmq
from zmq.auth.thread import ThreadAuthenticator

from ..base import ZmqBase
from .RepSocket import RepSocket
from .SubSocket import SubSocket, SubSocketAddress


class ZmqReceiver(ZmqBase):
    '''
    A ZmqReceiver class will listen on a REP or SUB socket for messages
    and will invoke a 'HandleIncomingMessage' method to process it.
    Subclasses should override that. A response must be implemented for
    REP sockets, but is useless for SUB sockets.
    '''

    def __init__(
            self,
            zmq_rep_bind_address: Optional[str] = None,
            zmq_sub_connect_addresses: Tuple[SubSocketAddress, ...] = None,
            recreate_timeout: Optional[int] = 600,
            username: Optional[str] = None,
            password: Optional[str] = None):
        super().__init__()
        self.__context = zmq.Context()
        self.__poller = zmq.Poller()

        self.__sub_sockets = tuple(
            SubSocket(
                ctx=self.__context,
                poller=self.__poller,
                address=address,
                timeout_in_sec=recreate_timeout,
            )
            for address in (zmq_sub_connect_addresses or tuple())
        )

        self.__auth: Optional[ThreadAuthenticator] = None
        if username is not None and password is not None:
            # Start an authenticator for this context.
            # Does not work on PUB/SUB as far as I know (probably because the
            # more secure solutions require two way communication as well)
            self.__auth = ThreadAuthenticator(self.__context)
            self.__auth.start()

            # Instruct authenticator to handle PLAIN requests
            self.__auth.configure_plain(
                domain='*',
                passwords={
                    username: password,
                }
            )

        self.__rep_socket = RepSocket(
            ctx=self.__context,
            poller=self.__poller,
            address=zmq_rep_bind_address,
            auth=self.__auth,
        ) if zmq_rep_bind_address else None

        self.__last_received_message = None
        self.__is_running = False

    def stop(self) -> None:
        '''
        May take up to 60 seconds to actually stop since poller has timeout of
        60 seconds
        '''

        self._info('Closing pub and sub sockets...')
        self.__is_running = False

        if self.__auth is not None:
            self.__auth.stop()

    def _run_rep_socket(self, socks) -> None:
        if self.__rep_socket is None:
            return

        incoming_message = self.__rep_socket.recv_string(socks)
        if incoming_message is None:
            return

        if incoming_message != self.HEARTBEAT_MSG:
            self.__last_received_message = incoming_message

        self._debug('Got info from REP socket')

        try:
            response_message = self.handle_incoming_message(
                incoming_message,
            )
            self.__rep_socket.send(response_message)
        except Exception as e:
            self._error(e)

    def _run_sub_sockets(self, socks) -> None:
        for sub_socket in self.__sub_sockets:
            incoming_message = sub_socket.recv_string(socks)

            if incoming_message is None:
                continue

            if incoming_message != self.HEARTBEAT_MSG:
                self.__last_received_message = incoming_message

            self._debug('Got info from SUB socket')

            try:
                self.handle_incoming_message(incoming_message)
            except Exception as e:
                self._error(e)

    def run(self) -> None:
        self.__is_running = True

        while self.__is_running:
            try:
                socks = dict(self.__poller.poll(1000))
            except BaseException as e:
                self._error(e)
                continue

            self._debug('Poll cycle over. checking sockets')
            self._run_rep_socket(socks)
            self._run_sub_sockets(socks)

        if self.__rep_socket:
            self.__rep_socket.destroy()

        for sub_socket in self.__sub_sockets:
            sub_socket.destroy()

    def create_response_message(
            self,
            status_code: int,
            status_message: str,
            response_message: Optional[str] = None) -> str:
        payload = {
            self.STATUS_CODE: status_code,
            self.STATUS_MSG: status_message,
        }

        if response_message is not None:
            payload[self.RESPONSE_MSG] = response_message

        return json.dumps(payload)

    def handle_incoming_message(self, message: str) -> Optional[str]:
        if message == self.HEARTBEAT_MSG:
            return None

        return self.create_response_message(
            status_code=self.STATUS_CODE_OK,
            status_message=self.STATUS_MSG_OK,
        )

    def get_last_received_message(self) -> Optional[str]:
        return self.__last_received_message

    def get_sub_socket(self, idx: int) -> SubSocket:
        return self.__sub_sockets[idx]
