'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''

import json

import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator

from ..logger import logger
from .RepSocket import RepSocket
from .SubSocket import SubSocket


class ZmqReceiver:
    '''
    A ZmqReceiver class will listen on a REP or SUB socket for messages
    and will invoke a 'HandleIncomingMessage' method to process it.
    Subclasses should override that. A response must be implemented for
    REP sockets, but is useless for SUB sockets.
    '''

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_sub_connect_addresses=None,
            recreate_sockets_on_timeout_of_sec=600,
            username=None,
            password=None):
        self.context = zmq.Context()
        self.auth = None
        self.last_received_message = None
        self.is_running = False
        self.thread = None
        self.zmq_rep_bind_address = zmq_rep_bind_address
        self.zmq_sub_connect_addresses = zmq_sub_connect_addresses
        self.poller = zmq.Poller()
        self.sub_sockets = []
        self.rep_socket = None
        if username is not None and password is not None:
            # Start an authenticator for this context.
            # Does not work on PUB/SUB as far as I (probably because the
            # more secure solutions require two way communication as well)
            self.auth = ThreadAuthenticator(self.context)
            self.auth.start()
            # Instruct authenticator to handle PLAIN requests
            self.auth.configure_plain(
                domain='*', passwords={username: password})

        if self.zmq_sub_connect_addresses:
            for address in self.zmq_sub_connect_addresses:
                self.sub_sockets.append(
                    SubSocket(
                        self.context,
                        self.poller,
                        address,
                        recreate_sockets_on_timeout_of_sec))
        if zmq_rep_bind_address:
            self.rep_socket = RepSocket(
                self.context,
                self.poller,
                zmq_rep_bind_address,
                self.auth)

    # May take up to 60 seconds to actually stop since poller has timeout of
    # 60 seconds
    def stop(self):
        self.is_running = False
        logger.info("Closing pub and sub sockets...")
        if self.auth is not None:
            self.auth.stop()

    def run(self):
        self.is_running = True

        while self.is_running:
            socks = dict(self.poller.poll(1000))
            logger.debug("Poll cycle over. checking sockets")
            if self.rep_socket:
                incoming_message = self.rep_socket.recv_string(socks)
                if incoming_message is not None:
                    self.last_received_message = incoming_message
                    try:
                        logger.debug("Got info from REP socket")
                        response_message = self.handle_incoming_message(
                            incoming_message)
                        self.rep_socket.send(response_message)
                    except Exception as e:
                        logger.error(e)
            for sub_socket in self.sub_sockets:
                incoming_message = sub_socket.recv_string(socks)
                if incoming_message is not None:
                    if incoming_message != "zmq_sub_heartbeat":
                        self.last_received_message = incoming_message
                    logger.debug("Got info from SUB socket")
                    try:
                        self.handle_incoming_message(incoming_message)
                    except Exception as e:
                        logger.error(e)

        if self.rep_socket:
            self.rep_socket.destroy()
        for sub_socket in self.sub_sockets:
            sub_socket.destroy()

    def create_response_message(
            self,
            status_code,
            status_message,
            response_message):
        if response_message is not None:
            return json.dumps({"status_code": status_code,
                               "status_message": status_message,
                               "response_message": response_message})
        else:
            return json.dumps({"status_code": status_code,
                               "status_message": status_message})

    def handle_incoming_message(self, message):
        if message != "zmq_sub_heartbeat":
            return self.create_response_message(200, "OK", None)
