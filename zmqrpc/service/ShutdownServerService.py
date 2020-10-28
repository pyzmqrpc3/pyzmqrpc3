

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from typing import Optional

from ..command import ShutdownServer
from ..receiver import ZmqReceiver
from ..service import IService


class ShutdownServerService(IService):

    def __init__(self, server: ZmqReceiver):
        super().__init__()

        self.__server = server

    def __call__(self, command: ShutdownServer) -> Optional[object]:
        self.__server.stop()
