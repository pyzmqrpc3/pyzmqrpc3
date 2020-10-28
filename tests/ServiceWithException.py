

from typing import Optional

from zmqrpc import IService

from .Command import Command
from .State import State


class ServiceWithException(IService):

    def __init__(self, state: State):
        super().__init__()

        self.__state = state

    def __call__(self, command: Command) -> Optional[object]:
        self.__state.last_param1 = 'Exception Raised'

        raise Exception('Something went wrong')
