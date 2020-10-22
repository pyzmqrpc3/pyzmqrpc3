'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread

from .ZmqRpcServer import ZmqRpcServer


class ZmqRpcServerThread(Thread):
    '''
    The same as a ZmqRpcServer implementation but implemented in a Thread
    environment.
    '''

    def __init__(
            self,
            zmq_rep_bind_address=None,
            zmq_sub_connect_addresses=None,
            rpc_functions=None,
            recreate_sockets_on_timeout_of_sec=60,
            username=None,
            password=None):
        super().__init__()

        self.__server = ZmqRpcServer(
            zmq_rep_bind_address=zmq_rep_bind_address,
            zmq_sub_connect_addresses=zmq_sub_connect_addresses,
            rpc_functions=rpc_functions,
            recreate_sockets_on_timeout_of_sec=recreate_sockets_on_timeout_of_sec,
            username=username,
            password=password,
        )

    def last_received_message(self):
        return self.__server.last_received_message

    def run(self)->None:
        self.__server.run()

    def stop(self)->None:
        self.__server.stop()
