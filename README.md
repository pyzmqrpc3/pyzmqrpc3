
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

For more example, see below and are included in the repository.
A unit test is also included.

## Rationale

Working with ZeroMQ is great.
It is fun, fast and simply works.
I use it right now for routing time-series samples from all sorts of
sampling devices to a central location on the internet.
All samplers use PUB sockets.
The samples are collected using a proxy app that bridges the internet
to a remote host via a password protected REQ/REP socket.
From there the samples are exposed via a PUB socket again.

I found I was repeating the same code over and over, so decided to make
a module.

## Requirements

1. It should be possible to create a network by simply starting apps and
configure them with the location of the end-points.
The apps will typically be started on a process level, however,
threading should also be supported.
2. Must have support for PUB/SUB (non-reliable, whoever is listening) and
REQ/REP sockets (reliable).
The latter should have support for time outs and automatic recreation of a
REQ socket if no message is received in the time out period.
3. If somewhere in the network there is connection failing, messages
should be automatically queued up to a certain queue size.
Right now, this has been implemented on the PUB/SUB interface.
4. Password protection is important when traversing non-secure networks.
However, no CURVE based protection is needed for now, just simple
username/password.
The fact that a network can be sniffed is not relevant for my specific use case.
5. Since I use a lot of Raspberry devices, it shall be able to work around
a bug (ARM only) that stops listening on SUB sockets when another device
connected via SUB disconnected.
This particular bug seems fixed in ZeroMQ 4.x, but not tested by me.
Leaving the code in for now.

## Components

### ZmqReceiver

Starts a loop listening via a SUB or REP socket for new messages.
Multiple SUB end-points may be provided.
If a message is received it calls 'HandleNewMessage' which can be
overridden by any subclassed implementation.

### ZmqClient

Upon creation it starts a PUB socket and/or creates a REQ socket.
The REQ socket may point to multiple end-points, which then use round-robin
message delivery.
The ZmqClient implements a 'send' method that sends a message.

### ZmqProxy

Forwards messages from a SUB --> REQ socket or from a PUB --> REP socket.

### ZmqRpcClient

Invokes a remotely implemented method over a PUB or REQ socket.
For PUB sockets no response messages can be expected.

### ZmqRpcServer

Implements a method that can be remotely invoked.
Uses ZmqReceiver functionality to listen for messages on a REP or SUB
socket, deserialize the message and invoke them.

## Available standard proxies

A number of already provided proxies are available:

* REQ to REQ by means of ZmqProxySub2ReqThread
* SUB to PUB by means of ZmqProxySub2PubThread
* REP to PUB by means of ZmqProxyRep2PubThread
* REP to REQ by means of ZmqProxyRep2ReqThread
* Buffered REP to REQ via ZmqBufferedProxyRep2ReqThread

Each of these proxies will take a message from the input format/socket and
proxy it to the output socket.
One model could be to collect all samples from all subprocesses on a site
and multiplex them via the proxy in a reliable manner over a REP/REQ socket.

Note that when a PUB/SUB connection is used, there is no return message or
in case of method invocation, any function response is discarded.

The buffered REP/REQ proxy quietly uses a PUB/SUB socket to introduce a
means to buffer messages and method invocations.

## Known issues

* Serialization is very limited and only supports types that can be serialized
over JSON.
* Only localhost type of testing done with passwords. Not sure if auth works
over remote connections

## Notes

Please note that this implementation is very pre-mature, although it works
fine for me in my own project and has operated stable for months.
