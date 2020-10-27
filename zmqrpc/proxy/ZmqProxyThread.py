

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from threading import Thread
from typing import Optional

from .ZmqProxy import ZmqProxy


class ZmqProxyThread(Thread):

    def __init__(self):
        super().__init__()

        self.__proxy: Optional[ZmqProxy] = None

    def _set_proxy(self, proxy: ZmqProxy) -> None:
        self.__proxy = proxy

    def get_last_received_message(self) -> Optional[str]:
        if self.__proxy is None:
            return None

        return self.__proxy.get_last_received_message()

    def run(self) -> None:
        if self.__proxy is None:
            return

        self.__proxy.run()

    def stop(self) -> None:
        if self.__proxy is None:
            return

        self.__proxy.stop()
