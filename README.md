
# pyzmqrpc3

![Publish](https://github.com/brgirgis/pyzmqrpc3/workflows/Publish/badge.svg)
![Test](https://github.com/brgirgis/pyzmqrpc3/workflows/Test/badge.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/pyzmqrpc3?period=week&units=international_system&left_color=black&right_color=orange&left_text=Last%20Week)](https://pepy.tech/project/pyzmqrpc3)
[![Downloads](https://static.pepy.tech/personalized-badge/pyzmqrpc3?period=month&units=international_system&left_color=black&right_color=orange&left_text=Month)](https://pepy.tech/project/pyzmqrpc3)
[![Downloads](https://static.pepy.tech/personalized-badge/pyzmqrpc3?period=total&units=international_system&left_color=black&right_color=orange&left_text=Total)](https://pepy.tech/project/pyzmqrpc3)

## Introduction

This Python package adds basic Remote Procedure Call (RPC) functionalities to
ZeroMQ.
The supported command/service architecture allows for complex serialization of
user defined data and modern-looking implementation.

## Install

    pip install pyzmqrpc3

## Usage

Implement a concrete class of the interface class `ICommand` that can
de/serialize itself and has a default constructor
(i.e. can be constructed without any arguments):

    from typing import Optional
    from zmqrpc import ICommand

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

The two methods, `set_command_state()` and `get_command_state()`, are
essential for marshaling the command data between the client and the server.
It is the user's responsibility to make sure that the implementation of these
methods is correct to avoid any data loss.
Both the client and the server side need to be aware of all the system
commands' implementations.

Implement a concrete service functor which inherits from `IService` and
handles one kind of a command by the server:

    from typing import Optional
    from zmqrpc import IService

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

Although it is technically possible to make one service to handle more
than one command,
it is highly recommended from architecture point of view to dedicate
one service for one command type.
Services' implementations need not to be visible on the client side
from code organization point of view.

On the server side, create a ZeroMQ RPC server:

    from zmqrpc import ZmqRpcServer

    server = ZmqRpcServer(
        zmq_rep_bind_address='tcp://*:30000',
    )

Register all the services:

    server.register_service(
        command_class=SimpleCommand,
        service=SimpleService(),
    )

Note that this call takes the ***actual*** command class and an ***instance***
of the service functor.

After registering all the services, start the RPC server:

    server.start()

On the client side, create a client that connects to that server endpoint:

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:30000'],
    )

Have the client execute commands on the server:

    client.execute_remote(
        command=SimpleCommand(param1='value1', param2='value2'),
    )

For more examples, take a look at the [examples](./examples) directory.
Even more examples can be found in the [tests](./tests) directory.

## Rationale

Working with ZeroMQ is great!
It is fun, fast and simply works.
It can be used with many applications out of the box with minimal effort.
However, there is no clear structure for the RPC workflow.
This package is a lightweight layer to bridge this gap with minimal restrictions
on what we can already do with the barebone ZMQ.

## Requirements

1. It should be possible to create a network by simply starting apps and
configure them with the location of the end-points.
The apps will typically be started on a process level, however,
threading should also be supported.
2. Must have support for PUB/SUB (non-reliable, whoever is listening) and
REQ/REP sockets (reliable).
The latter should have support for timeouts and automatic recreation of a
REQ socket if no message is received in the timeout period.
3. If somewhere in the network there is connection failing, messages
should be automatically queued up to a certain queue size.
Right now, this has been implemented on the PUB/SUB interface.
4. Password protection is important when traversing non-secure networks.
However, no CURVE based protection is needed for now, just simple
username/password.
The fact that a network can be sniffed is not relevant for general use cases.
5. Since it is common to use a lot of devices together, like Raspberry devices,
it shall be able to work around via proxy connections.

## Components

### ZmqReceiver/Thread

Starts a loop listening via a SUB or REP socket for new messages.
Multiple SUB end-points may be provided.
If a message is received, it calls the `handle_incoming_message()` method
which can be overridden by any subclassed implementation.

The thread version, `ZmqReceiverThread`, can be used for testing or with
applications that might be running multiple server threads.

### ZmqSender

Upon creation it starts a PUB socket and/or creates a REQ socket.
The REQ socket may point to multiple end-points, which then use round-robin
message delivery.
The ZmqSender implements the `send()` method that sends a message.

### ZmqProxy

Forwards messages from a SUB --> REQ socket or from a PUB --> REP socket using
a receiver/sender pair.

### ZmqRpcServer/Thread

Implements service(s) that can be remotely executed by receiving a distinct
command type.
It inherits the `ZmqReceiver` functionality to listen for messages on a
REP or SUB socket.
However, it overrides the `handle_incoming_message()` method to deserialize
command messages, identify their type and execute the corresponding service
implementation.

The thread version, `ZmqRpcServerThread`, can be used for testing or with
applications that might be running multiple server threads.

### ZmqRpcClient

Executes a remotely implemented service over a PUB or REQ socket using a
command argument.
For PUB sockets, no response messages should be expected.
It inherits the `ZmqSender` functionality to send messages over the wire.

### ICommand

The base interface class for all concrete command types.
It enforces the implementation of two methods; `set_command_state()` and
`get_command_state()`.
These two methods are essential in marshaling any complex user data from the
client side to the server side.

### IService

The base interface class for all concrete service functors.
It enforces the implementation of the `__call__()` method which is the entry
point of handling a certain command type on the server side.

## Available Standard Proxies

A number of proxies are available out of the box:

* REQ to REQ by means of ZmqProxySub2Req/Thread
* SUB to PUB by means of ZmqProxySub2Pub/Thread
* REP to PUB by means of ZmqProxyRep2Pub/Thread
* REP to REQ by means of ZmqProxyRep2Req/Thread
* Buffered REP to REQ via ZmqBufferedProxyRep2ReqThread

Each of these proxies/proxy-threads will take a message from the input
format/socket and marshal it to the output socket.
One model could be to collect all samples from all sub-processes on a site
and multiplex them via the proxy in a reliable manner over a REP/REQ socket.

Note that when a PUB/SUB connection is used, there is no return message or
in case of method invocation, any function response is discarded.

The buffered REP/REQ proxy quietly uses a PUB/SUB socket to introduce a
means to buffer messages and method invocations.

## Known Issues and Limitations (KIL)

* Only localhost type of testing done with passwords.
Not sure if auth works over remote connections.
* The `inproc://` transport of ZMQ is not supported by current implementation.

## Notes

Please note that this implementation is very pre-mature, although it works
fine for the projects it is currently being used in and has operated stable
for months.
