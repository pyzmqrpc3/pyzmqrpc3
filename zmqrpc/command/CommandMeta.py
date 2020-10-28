

'''
Created on Oct 2020

@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from .CommandDatabase import command_database


class CommandMeta(type):

    def __new__(cls, name, parents, dct):
        # we need to call type.__new__ to complete the initialization
        return super().__new__(cls, name, parents, dct)

    def __init__(cls, name, bases, dct):
        """
         we use __init__ rather than __new__ here because we want
         to modify attributes of the class *after* they have been
         created
        """

        super().__init__(name, bases, dct)

        if name == 'ICommand':
            return

        command_database.register_command(name, cls)
