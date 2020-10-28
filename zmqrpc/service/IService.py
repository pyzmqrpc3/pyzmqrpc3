

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from abc import ABCMeta, abstractmethod
from typing import Optional

from ..command import ICommand


class IService(metaclass=ABCMeta):

    @abstractmethod
    def __call__(self, command: ICommand) -> Optional[object]:
        pass
