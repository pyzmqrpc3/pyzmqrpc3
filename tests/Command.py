

from typing import Optional

from zmqrpc import ICommand


class Command(ICommand):

    def __init__(
            self,
            param1: Optional[str] = None,
            param2: Optional[str] = None):
        super().__init__()

        self.__param1 = param1 or ''
        self.__param2 = param2 or ''

    @property
    def param1(self) -> str:
        return self.__param1

    @property
    def param2(self) -> str:
        return self.__param2

    def set_command_state(self, state: dict) -> None:
        self.__param1 = state['param1']
        self.__param2 = state['param2']

    def get_command_state(self) -> dict:
        return dict(
            param1=self.param1,
            param2=self.param2,
        )
