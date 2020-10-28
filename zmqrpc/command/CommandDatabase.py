

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


class CommandDatabase:

    def __init__(self):
        self.__commands = {}

    @property
    def commands(self) -> dict:
        return self.__commands

    def register_command(self, name: str, command_class: object) -> None:
        if name in self.commands:
            raise RuntimeError('found a repeated command name: "%s"' % name)

        self.__commands[name] = command_class

    def __getattr__(self, attrib: str) -> object:
        if attrib in self.commands:
            return self.commands[attrib]

        raise RuntimeError(
            'could not find command "%s" in the commands database' %
            attrib
        )

    def __getitem__(self, attrib: str) -> object:
        if attrib in self.commands:
            return self.commands[attrib]

        raise RuntimeError(
            'could not find command "%s" in the commands database' %
            attrib
        )


command_database = CommandDatabase()
