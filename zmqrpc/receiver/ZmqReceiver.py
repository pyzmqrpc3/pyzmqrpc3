

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
from typing import Optional, Tuple

import zmq
from zmq.auth.thread import ThreadAuthenticator

from ..heartbeat import zmq_sub_heartbeat
from ..logger import logger
from .RepSocket import RepSocket
from .SubSocket import SubSocket, SubSocketAddress


class ZmqReceiver:
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
            recreate_timeout: int = 600,
            username: Optional[str] = None,
            password: Optional[str] = None):
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

        logger.info('Closing pub and sub sockets...')
        self.__is_running = False

        if self.__auth is not None:
            self.__auth.stop()

    def run(self) -> None:
        self.__is_running = True

        while self.__is_running:
            socks = dict(self.__poller.poll(1000))

            logger.debug('Poll cycle over. checking sockets')

            if self.__rep_socket:
                incoming_message = self.__rep_socket.recv_string(socks)
                if incoming_message is not None:
                    self.__last_received_message = incoming_message

                    try:
                        logger.debug('Got info from REP socket')

                        response_message = self.handle_incoming_message(
                            incoming_message,
                        )

                        self.__rep_socket.send(response_message)
                    except Exception as e:
                        logger.error(e)

            for sub_socket in self.__sub_sockets:
                incoming_message = sub_socket.recv_string(socks)

                if incoming_message is not None:

                    if incoming_message != zmq_sub_heartbeat:
                        self.__last_received_message = incoming_message

                    logger.debug("Got info from SUB socket")

                    try:
                        self.handle_incoming_message(incoming_message)
                    except Exception as e:
                        logger.error(e)

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
            'status_code': status_code,
            'status_message': status_message,
        }

        if response_message is not None:
            payload['response_message'] = response_message

        return json.dumps(payload)

    def handle_incoming_message(self, message: str) -> Optional[str]:
        if message == zmq_sub_heartbeat:
            return None

        return self.create_response_message(
            status_code=200,
            status_message='OK',
        )

    def get_last_received_message(self) -> Optional[str]:
        return self.__last_received_message

    def get_sub_socket(self, idx: int) -> SubSocket:
        return self.__sub_sockets[idx]
