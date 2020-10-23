
# Examples

This example is from demo_pub_sub.py. It should be relatively
self explanatory.
It starts an RPC server thread, registers a function, then creates an RPC
client and invokes the registered function.

    from zmqrpc.ZmqRpcClient import ZmqRpcClient
    from zmqrpc.ZmqRpcServer import ZmqRpcServerThread
    import time
    
    
    def test_method(param1, param2):
        print "test_method invoked with params '{0}' and '{1}'".format(param1, param2)
    
    if __name__ == '__main__':
        client = ZmqRpcClient(
            zmq_pub_endpoint="tcp://*:30000",
            username="test",
            password="test")
    
        server = ZmqRpcServerThread(
            zmq_sub_connect_addresses=["tcp://localhost:30000"],    # Must be a list
            rpc_functions={"test_method": test_method},             # Dict
            username="test",
            password="test")
    
        server.start()
    
        # Wait a bit since sockets may not have been connected immediately
        time.sleep(2)
    
        client.invoke(
            function_name="test_method",
            function_parameters={"param1": "param1", "param2": "param2"})   # Must be dict
    
        # Wait a bit to make sure message has been received
        time.sleep(2)
    
        # Clean up
        server.stop()
        server.join()

Example with invoking method in REP/REQ.
The difference with PUB/SUB is that this will return a response message:

    from zmqrpc.ZmqRpcClient import ZmqRpcClient
    from zmqrpc.ZmqRpcServer import ZmqRpcServerThread
    import time
    
    
    def test_method(param1, param2):
        print "test_method invoked with params '{0}' and '{1}'".format(param1, param2)
        return "test_method response text"
    
    if __name__ == '__main__':
        client = ZmqRpcClient(
            zmq_req_endpoints=["tcp://localhost:30000"],            # List
            username="test",
            password="test")
    
        server = ZmqRpcServerThread(
            zmq_rep_bind_address="tcp://*:30000",
            rpc_functions={"test_method": test_method},             # Dict
            username="test",
            password="test")
        server.start()
    
        # Wait a bit since sockets may not have been connected immediately
        time.sleep(2)
    
        # REQ/REQ sockets can carry a response
        response = client.invoke(
            function_name="test_method",
            function_parameters={"param1": "param1", "param2": "param2"})   # Must be dict
    
        print "response: {0}".format(response)
    
        # Wait a bit to make sure message has been received
        time.sleep(2)
    
        # Clean up
        server.stop()
        server.join()

## New since 1.5.0 - Per socket heartbeats

In order to detect silently disconnected SUB sockets
(network failures or otherwise), it is now possible to (optionally) define a
heartbeat timeout per SUB socket.
Updated example:

        server = ZmqRpcServerThread(
            zmq_sub_connect_addresses=[("tcp://localhost:30000", 60)],
            rpc_functions={"test_method": test_method},
            username="test",
            password="test")

Per SUB socket address a tuple can be specified that holds the address as
the first element and the heartbeat timeout as the second.
Note that that the responsibility to send an heartbeat 
