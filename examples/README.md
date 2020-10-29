
# Examples

This example is from demo_pub_sub.py.
t should be relatively self explanatory.
It starts an RPC server thread, registers a command/service pair,
then creates an RPC client and execute the registered command.

    import sys
    import time
    from typing import Optional, Tuple

    from zmqrpc import ICommand, IService, ZmqRpcClient, ZmqRpcServerThread


    class SimpleCommand(ICommand):

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


    class SimpleService(IService):

        def __call__(self, command: SimpleCommand) -> Optional[object]:
            print(
                'SimpleCommand executed with params "{0}" and "{1}"'.format(
                    command.param1,
                    command.param2,
                )
            )
            return 'SimpleService response text for SimpleCommand is "%s"' % str(
                dict(
                    param1=command.param1,
                    param2=command.param2,
                )
            )


    def main(args: Optional[Tuple[str]] = None) -> int:

        print('starting client ...')
        client = ZmqRpcClient(
            zmq_pub_endpoint='tcp://*:30000',
        )

        print('starting server ...')
        server = ZmqRpcServerThread(
            zmq_sub_connect_addresses=['tcp://localhost:30000'],    # Must be a list
        )
        server.register_service(
            command_class=SimpleCommand,
            service=SimpleService(),
        )
        server.start()

        # Wait a bit since sockets may not have been connected immediately
        time.sleep(2)

        response = client.execute_remote(
            command=SimpleCommand(param1='value1', param2='value2'),
        )

        print('response: {0}'.format(response))

        # Wait a bit to make sure message has been received
        time.sleep(2)

        # Clean up
        server.stop()
        server.join()

        client.destroy()

        return 0


    if __name__ == '__main__':
        sys.exit(main())

Running this demo should give an output similar to this:

    starting client ...
    starting server ...
    response: None
    SimpleCommand executed with params "value1" and "value2"

Example with executing commands in REP/REQ.
The difference with PUB/SUB is that this will return a response message:

    import sys
    import time
    from typing import Optional, Tuple

    from zmqrpc import ICommand, IService, ZmqRpcClient, ZmqRpcServerThread


    class SimpleCommand(ICommand):

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


    class SimpleService(IService):

        def __call__(self, command: SimpleCommand) -> Optional[object]:
            print(
                'SimpleCommand executed with params "{0}" and "{1}"'.format(
                    command.param1,
                    command.param2,
                )
            )
            return 'SimpleService response text for SimpleCommand is "%s"' % str(
                dict(
                    param1=command.param1,
                    param2=command.param2,
                )
            )


    def main(args: Optional[Tuple[str]] = None) -> int:

        print('starting client ...')
        client = ZmqRpcClient(
            zmq_req_endpoints=['tcp://localhost:30000'],            # List
            username='test',
            password='test',
        )

        print('starting server ...')
        server = ZmqRpcServerThread(
            zmq_rep_bind_address='tcp://*:30000',
            username='test',
            password='test',
        )
        server.register_service(
            command_class=SimpleCommand,
            service=SimpleService(),
        )
        server.start()

        # Wait a bit since sockets may not have been connected immediately
        time.sleep(2)

        # REQ/REQ sockets can carry a response
        response = client.execute_remote(
            command=SimpleCommand(param1='passed param1', param2='passed param2'),
        )

        print('response: {0}'.format(response[0]))

        # Wait a bit to make sure message has been received
        time.sleep(2)

        # Clean up
        server.stop()
        server.join()

        client.destroy()

        return 0


    if __name__ == '__main__':
        sys.exit(main())

Running this demo should give an output similar to this:

    starting client ...
    starting server ...
    SimpleCommand executed with params "passed param1" and "passed param2"
    response: SimpleService response text for SimpleCommand is "{'param1': 'passed param1', 'param2': 'passed param2'}"

## New since 1.5.0 - Per socket heartbeats

In order to detect silently disconnected SUB sockets
(network failures or otherwise), it is now possible to (optionally) define a
heartbeat timeout per SUB socket.
Updated example:

    server = ZmqRpcServerThread(
        zmq_sub_connect_addresses=[('tcp://localhost:30000', 60)],
        username='test',
        password='test',
    )

Per SUB socket address a tuple can be specified that holds the address as
the first element and the heartbeat timeout as the second.
