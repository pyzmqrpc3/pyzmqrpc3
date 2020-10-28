

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from json import JSONEncoder

from .CommandDatabase import command_database
from .ICommand import ICommand


class JsonEncoder(JSONEncoder):

    ICommandKey = '_icmd_'

    def default(self, o):
        obj = o

        if isinstance(obj, ICommand):
            return {
                self.ICommandKey: (
                    type(obj).__name__,
                    obj.get_command_state(),
                ),
            }

        return super().default(obj)

    @ staticmethod
    def object_hook(d):

        if not isinstance(d, dict):
            return d

        if JsonEncoder.ICommandKey in d:
            name, state = d[JsonEncoder.ICommandKey]
            command = command_database.commands[name]()
            command.set_command_state(state=state)
            return command

        return d
