

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .ICommand import ICommand


class ShutdownServer(ICommand):

    def set_command_state(self, state: dict) -> None:
        pass

    def get_command_state(self) -> dict:
        return {}
