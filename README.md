
# pyzmqrpc3

![Publish](https://github.com/brgirgis/pyzmqrpc3/workflows/Publish/badge.svg)
![Test](https://github.com/brgirgis/pyzmqrpc3/workflows/Test/badge.svg)

## Introduction

This Python package adds basic Remote Procedure Call (RPC) functionalities to
ZeroMQ.
It does not do advanced serializing, but simply uses JSON call and
response structures.

## Install

    pip install pyzmqrpc3

## Usage

Implement a function on the server that can be invoked:

    def test_method(param1, param2):
        return param1 + param2

Create a ZeroMQ server:

    server = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:30000',
        rpc_functions={
            'test_method': test_method,
        },
    )
    server.start()

Create a client that connects to that server endpoint:

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:30000'],
    )

Have the client invoke the function on the server:

    client.invoke(
        function_name='test_method',
        function_parameters={
            "param1": "Hello",
            "param2": " world",
        },
    )

For more example, look at the [examples](./examples) directory.
More examples can also be found in the [tests](./tests) directory.

## Rationale

Working with ZeroMQ is great.
It is fun, fast and simply works.
It can be used with many applications out of the box with minimal effort.
However, there is no clear structure for RPC workflow.
This package is a lightweight layer to bridge this gap with minimal restrictions
on what we can already do with barebone ZMQ.

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

### ZmqReceiver

Starts a loop listening via a SUB or REP socket for new messages.
Multiple SUB end-points may be provided.
If a message is received it calls `ZmqReceiver.handle_incoming_message()`
which can be overridden by any subclassed implementation.

### ZmqClient

Upon creation it starts a PUB socket and/or creates a REQ socket.
The REQ socket may point to multiple end-points, which then use round-robin
message delivery.
The ZmqClient implements the `ZmqClient.send()` method that sends a message.

### ZmqProxy

Forwards messages from a SUB --> REQ socket or from a PUB --> REP socket using
a receiver/sender pair.

### ZmqRpcClient

Invokes a remotely implemented method over a PUB or REQ socket.
For PUB sockets, no response messages should be expected.

### ZmqRpcServer

Implements a method that can be remotely invoked.
It inherits the ZmqReceiver functionality to listen for messages on a
REP or SUB socket, deserialize the message and invoke them.

## Available Standard Proxies

A number of proxies are available out of the box:

* REQ to REQ by means of ZmqProxySub2Req/Thread
* SUB to PUB by means of ZmqProxySub2Pub/Thread
* REP to PUB by means of ZmqProxyRep2Pub/Thread
* REP to REQ by means of ZmqProxyRep2Req/Thread
* Buffered REP to REQ via ZmqBufferedProxyRep2ReqThread

Each of these proxies/proxy threads will take a message from the input
format/socket and marshal it to the output socket.
One model could be to collect all samples from all sub-processes on a site
and multiplex them via the proxy in a reliable manner over a REP/REQ socket.

Note that when a PUB/SUB connection is used, there is no return message or
in case of method invocation, any function response is discarded.

The buffered REP/REQ proxy quietly uses a PUB/SUB socket to introduce a
means to buffer messages and method invocations.

## Known Issues and Limitations (KIL)

* Serialization is very limited and only supports types that can be serialized
over JSON.
* Only localhost type of testing done with passwords.
Not sure if auth works over remote connections.
* The `inproc://` transport of ZMQ is not supported by current implementation.

## Notes

Please note that this implementation is very pre-mature, although it works
fine for the projects it is currently being used in and has operated stable
for months.
