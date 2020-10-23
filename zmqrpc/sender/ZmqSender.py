

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import json
import time
from typing import Optional

import zmq

from ..heartbeat import zmq_sub_heartbeat
from ..logger import logger


class ZmqSender:
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
            zmq_req_endpoints=None,
            zmq_pub_endpoint=None,
            username: Optional[str] = None,
            password: Optional[str] = None):
        self.context = zmq.Context()
        self.poller = zmq.Poller()

        self.username = username
        self.password = password

        self.zmq_req_endpoints = zmq_req_endpoints
        self.zmq_pub_endpoint = zmq_pub_endpoint

        self.pub_socket = None
        self.req_socket = None

        self.recreate_pub_socket = False
        self.recreate_req_socket = False

        self.create_pub_socket()
        self.create_req_socket()

        # 'Prevent' slow joiner problem
        time.sleep(0.5)

    def destroy_req_socket(self) -> None:
        error_message = None
        if self.req_socket is not None:
            try:
                self.poller.unregister(self.req_socket)
            except Exception as e:
                error_message = "Cannot un-register REQ socket to poller. "
                "Exception: {0}".format(e)
            try:
                self.req_socket.setsockopt(zmq.LINGER, 0)
            except Exception as e:
                error_message = "Cannot set LINGER socket option. "
                "Exception: {0}".format(e)
            try:
                for endpoint in self.zmq_req_endpoints:
                    logger.debug("Disconnect REQ socket to %s", endpoint)
                    self.req_socket.disconnect(endpoint)
            except Exception as e:
                error_message = "Cannot disconnect REQ socket. "
                "Exception: {0}".format(e)
            try:
                logger.debug("Close REQ socket to %s", self.zmq_req_endpoints)
                self.req_socket.close()
            except Exception as e:
                error_message = "Cannot close REQ socket. "
                "Exception: {0}".format(e)
        self.req_socket = None
        if error_message is not None:
            logger.error(error_message)

    def destroy_pub_socket(self) -> None:
        error_message = None
        if self.pub_socket is not None:
            try:
                self.pub_socket.setsockopt(zmq.LINGER, 0)
            except Exception as e:
                error_message = "Cannot set LINGER socket option. "
                "Exception: {0}".format(e)
            try:
                address = self.zmq_pub_endpoint
                # Since some recent version of pyzmq it does not accept unbind
                # of an address with '*'. Replace it with 0.0.0.0
                if '*' in address:
                    address = address.replace('*', '0.0.0.0')
                logger.debug("Unbind PUB socket to %s", self.zmq_pub_endpoint)
                self.pub_socket.unbind(address)
            except Exception as e:
                raise Exception(
                    "Cannot unbind PUB socket from {0}.".format(
                        self.zmq_pub_endpoint)
                ) from e
            try:
                logger.debug("Close PUB socket to %s", self.zmq_pub_endpoint)
                self.pub_socket.close()
            except Exception as e:
                error_message = "Cannot close PUB socket. "
                "Exception: {0}".format(e)
        self.pub_socket = None
        if error_message is not None:
            logger.error(error_message)

    def create_req_socket(self) -> None:
        if self.req_socket is not None:
            raise RuntimeError(
                "Want create new REQ socket, but old REQ Socket is "
                "not destroyed.")

        if self.zmq_req_endpoints:
            self.req_socket = self.context.socket(zmq.REQ)
            if self.username and self.password:
                try:
                    self.req_socket.setsockopt_string(
                        zmq.PLAIN_USERNAME,
                        self.username,
                    )

                    self.req_socket.setsockopt_string(
                        zmq.PLAIN_PASSWORD,
                        self.password,
                    )
                except TypeError:
                    # In case of python 2.
                    self.req_socket.setsockopt(
                        zmq.PLAIN_USERNAME,
                        self.username,
                    )

                    self.req_socket.setsockopt(
                        zmq.PLAIN_PASSWORD,
                        self.password,
                    )
            try:
                for endpoint in self.zmq_req_endpoints:
                    logger.debug("Connect REQ socket to %s", endpoint)
                    self.req_socket.connect(endpoint)
            except Exception as e:
                raise Exception(
                    "Cannot connect REQ socket to {0}.".format(
                        self.zmq_req_endpoints)
                ) from e
            try:
                self.poller.register(self.req_socket, zmq.POLLIN)
            except Exception as e:
                raise Exception(
                    "Cannot register REQ socket to poller. ") from e

    def create_pub_socket(self) -> None:
        if self.pub_socket is not None:
            raise RuntimeError(
                "Want create new PUB socket, but old PUB Socket is not "
                "destroyed."
            )

        if self.zmq_pub_endpoint:
            self.pub_socket = self.context.socket(zmq.PUB)
            if self.username and self.password:
                self.pub_socket.plain_username = self.username
                self.pub_socket.plain_password = self.password
            # Make sure we buffer enough (100000 messages) in case of network
            # troubles...
            self.pub_socket.setsockopt(zmq.SNDHWM, 100000)
            try:
                logger.debug("Bind PUB socket to %s", self.zmq_pub_endpoint)
                self.pub_socket.bind(self.zmq_pub_endpoint)
            except Exception as e:
                raise Exception(
                    "Cannot bind PUB socket to {0}.".format(
                        self.zmq_pub_endpoint)
                ) from e

    def _send_over_pub_socket(self, message) -> None:
        if self.pub_socket is not None:
            try:
                self.pub_socket.send_string(message)
            except Exception as e:
                self.recreate_pub_socket = True
                raise RuntimeError(
                    "Cannot send message on PUB socket. Highly exceptional. "
                    "Mark PUB socket for renewal. Consider this message "
                    "lost.") from e

    def handle_response(self, response_message_json) -> Optional[str]:
        try:
            response_message_dict = json.loads(response_message_json)
        except BaseException as e:
            raise Exception(
                "Marshalling error: Response is not a json message") from e
        else:
            if "status_code" not in response_message_dict:
                raise Exception("No status_code in response")

            if response_message_dict["status_code"] == 200 and \
                    "response_message" in response_message_dict:
                return response_message_dict["response_message"]

            if response_message_dict["status_code"] != 200 and \
                    "status_message" in response_message_dict:
                raise Exception(response_message_dict["status_message"])

            if response_message_dict["status_code"] != 200 and \
                    "status_message" not in response_message_dict:
                raise Exception(
                    "Error occurred with code {0}".format(
                        response_message_dict["status_code"]))

    def _send_over_req_socket(
            self,
            message: str,
            time_out_in_sec: int = 10) -> Optional[str]:
        if self.req_socket is None:
            return

        try:
            self.req_socket.send_string(message)
        except Exception as e:
            self.recreate_req_socket = True
            raise Exception(
                "Cannot send message on REQ socket. This is very "
                "exceptional. Please check logs. Marking REQ socket "
                "to be recreated on next try. Message can be considered "
                "lost.") from e
        else:
            # Wait for given time to receive response.
            start_time = time.time()
            while start_time + time_out_in_sec > time.time():
                # X seconds timeout before quiting on waiting for response
                req_socks = dict(self.poller.poll(1000))
                if req_socks.get(self.req_socket) == zmq.POLLIN:
                    try:
                        response_message_json = self.req_socket.recv_string()
                    except Exception as e:
                        logger.error(
                            "Could not receive message from socket. "
                            "Marking REQ socket to be recreated on next "
                            "try. Exception: %s", e)
                        self.recreate_req_socket = True
                    else:
                        return self.handle_response(response_message_json)
            # Some unexpected socket related error occurred. Recreate the
            # REQ socket.
            self.recreate_req_socket = True
            raise Exception(
                "No response received on ZMQ Request to end point"
                " {0} in {1} seconds. Discarding message. Marking REQ "
                "socket to be recreated on next try.".format(
                    self.zmq_req_endpoints,
                    time_out_in_sec,
                )
            )

    def send(
            self,
            message: str,
            time_out_in_sec: int = 60) -> Optional[str]:
        # Create sockets if needed. Raise an exception if any problems are
        # encountered
        if self.recreate_pub_socket:
            self.destroy_pub_socket()
            self.create_pub_socket()
            self.recreate_pub_socket = False

        if self.recreate_req_socket:
            self.destroy_req_socket()
            self.create_req_socket()
            self.recreate_req_socket = False

        # Sockets must exist otherwise we would not be here...
        # Any errors in the following lines will throw an error that must be
        # caught
        self._send_over_pub_socket(message)
        return self._send_over_req_socket(
            message,
            time_out_in_sec,
        )

    def send_heartbeat(self) -> None:
        self.send(zmq_sub_heartbeat)

    def destroy(self) -> None:
        self.destroy_req_socket()
        self.destroy_pub_socket()
