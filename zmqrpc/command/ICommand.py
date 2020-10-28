

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .CommandMeta import CommandMeta


class ICommand(metaclass=CommandMeta):

    def set_command_state(self, state: dict) -> None:
        assert False

    def get_command_state(self) -> dict:
        assert False
