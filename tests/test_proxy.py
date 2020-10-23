

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


def test_11_rpc1_req_rep_with_rep_req_proxy_without_password(self):
    # RPC invoke method over REQ/REP sockets with an extra rep/req proxy in
    # between
    print("Test if invoking a method works over REQ/REP RPC socket, using an extra rep/req proxy")

    client = ZmqRpcClient(zmq_req_endpoints=["tcp://localhost:53000"])

    proxy_rep_req_thread = ZmqProxyRep2ReqThread(
        zmq_rep_bind_address='tcp://*:53000',
        zmq_req_connect_addresses=["tcp://localhost:53001"])
    proxy_rep_req_thread.start()

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address="tcp://*:53001",
        rpc_functions={
            "invoke_test": invoke_test})
    server_thread.start()

    time.sleep(1)

    response = client.invoke(
        function_name="invoke_test",
        function_parameters={
            "param1": "value1",
            "param2": "value2"},
        time_out_in_sec=3)

    server_thread.stop()
    server_thread.join()
    proxy_rep_req_thread.stop()
    proxy_rep_req_thread.join()
    client.destroy()
    # Cleaning up sockets takes some time
    time.sleep(1)

    self.assertEquals(response, "value1:value2")


def test_12_rpc1_req_rep_with_rep_req_proxy(self):
    # RPC invoke method over REQ/REP sockets with an extra rep/req proxy in
    # between
    print("Test if invoking a method works over REQ/REP RPC socket, includes a username/password and also an extra rep/req proxy")

    client = ZmqRpcClient(
        zmq_req_endpoints=["tcp://localhost:52000"],
        username="username",
        password="password")

    proxy_rep_req_thread = ZmqProxyRep2ReqThread(
        zmq_rep_bind_address='tcp://*:52000',
        zmq_req_connect_addresses=["tcp://localhost:52001"],
        username_rep="username",
        password_rep="password",
        username_req="username2",
        password_req="password2")
    proxy_rep_req_thread.start()

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address="tcp://*:52001",
        rpc_functions={
            "invoke_test": invoke_test},
        username="username2",
        password="password2")
    server_thread.start()

    response = client.invoke(
        function_name="invoke_test",
        function_parameters={
            "param1": "value1",
            "param2": "value2"},
        time_out_in_sec=3)

    server_thread.stop()
    server_thread.join()
    proxy_rep_req_thread.stop()
    proxy_rep_req_thread.join()
    client.destroy()
    # Cleaning up sockets takes some time
    time.sleep(1)

    self.assertEquals(response, "value1:value2")


def test_13_rpc1_pub_sub_with_pub_sub_proxy(self):
    # RPC invoke method over PUB/SUB sockets and a PUB/SUB proxy
    print("Test if invoking a method works over PUB/SUB RPC socket and a PUB/SUB proxy in between")
    server_thread = ZmqRpcServerThread(
        zmq_sub_connect_addresses=["tcp://localhost:4567"],
        rpc_functions={
            "invoke_test": invoke_test})
    server_thread.start()

    proxy_pub_sub_thread = ZmqProxySub2PubThread(
        zmq_pub_bind_address="tcp://*:4567",
        zmq_sub_connect_addresses=['tcp://localhost:4566'])
    proxy_pub_sub_thread.start()

    client = ZmqRpcClient(zmq_pub_endpoint="tcp://*:4566")
    # Wait a bit to avoid slow joiner...
    time.sleep(1)

    response = client.invoke(
        function_name="invoke_test",
        function_parameters={
            "param1": "value2sub",
            "param2": "value2pub"},
        time_out_in_sec=3)

    # Wait a bit to make sure message is sent...
    time.sleep(1)

    server_thread.stop()
    server_thread.join()
    proxy_pub_sub_thread.stop()
    proxy_pub_sub_thread.join()
    client.destroy()
    # Cleaning up sockets takes some time
    time.sleep(1)

    # Response should be empty with PUB/SUB
    self.assertEquals(response, None)
    self.assertEquals(call_state.last_invoked_param1, "value2sub")


def test_14_proxy(self):
    # With proxy elements
    print(
        "Add a proxy setup to the end to end chain pub->proxy.req->proxy.rep->pub->sub")
    sender = ZmqSender(zmq_pub_endpoint="tcp://*:57000")

    proxy_sub_req_thread = ZmqProxySub2ReqThread(
        zmq_sub_connect_addresses=['tcp://localhost:57000'],
        zmq_req_connect_addresses=["tcp://localhost:57001"],
        username_req="username",
        password_req="password")
    proxy_sub_req_thread.start()

    proxy_rep_pub_thread = ZmqProxyRep2PubThread(
        zmq_rep_bind_address='tcp://*:57001',
        zmq_pub_bind_address='tcp://*:57002',
        username_rep="username",
        password_rep="password")
    proxy_rep_pub_thread.start()

    receiver_thread = ZmqReceiverThread(
        zmq_sub_connect_addresses=["tcp://localhost:57002"])
    receiver_thread.start()
    # Take 0.5 second for sockets to connect to prevent 'slow joiner'
    # problem
    time.sleep(0.5)

    sender.send("test")
    # Sleep for pub/sub not guaranteed to be done on completing
    # send_pub_socket
    time.sleep(1)
    print("last received message by proxy_sub_req_thread: {0}".format(
        proxy_sub_req_thread.get_last_received_message()))
    print("last received message by proxy_rep_pub_thread: {0}".format(
        proxy_rep_pub_thread.get_last_received_message()))
    print("last received message by receiver_thread: {0}".format(
        receiver_thread.get_last_received_message()))

    self.assertEqual(receiver_thread.get_last_received_message(), 'test')

    receiver_thread.stop()
    receiver_thread.join()
    proxy_sub_req_thread.stop()
    proxy_sub_req_thread.join()
    proxy_rep_pub_thread.stop()
    proxy_rep_pub_thread.join()
    sender.destroy()
    # Cleaning up sockets takes some time
    time.sleep(1)


def test_15_rpc1_req_rep_with_rep_req_buffered_proxy(self):
    # RPC invoke method over REQ/REP sockets with an extra rep/req proxy in
    # between
    print("Test if invoking a method works over Buffered REQ/REP RPC socket, includes a username/password")

    call_state.last_invoked_param1 = None
    client = ZmqRpcClient(
        zmq_req_endpoints=["tcp://localhost:51000"],
        username="username",
        password="password")

    buf_proxy_rep_req_thread = ZmqBufferedProxyRep2ReqThread(
        zmq_rep_bind_address='tcp://*:51000',
        zmq_req_connect_addresses=["tcp://localhost:51001"],
        buffered_pub_address="tcp://*:59878",
        buffered_sub_address="tcp://localhost:59878",
        username_rep="username",
        password_rep="password",
        username_req="username2",
        password_req="password2")
    buf_proxy_rep_req_thread.start()

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address="tcp://*:51001",
        rpc_functions={
            "invoke_test": invoke_test},
        username="username2",
        password="password2")
    server_thread.start()

    time.sleep(1)

    response = client.invoke(
        function_name="invoke_test",
        function_parameters={
            "param1": "value1viaproxy",
            "param2": "value2viaproxy"},
        time_out_in_sec=30)

    time.sleep(1)

    self.assertEquals(response, None)
    self.assertEquals(call_state.last_invoked_param1, "value1viaproxy")

    # Now send a couple of messages while nothing is receiving to validate
    # buffering is owrking fine
    server_thread.stop()
    server_thread.join()

    call_state.last_invoked_param1 = None
    response = client.invoke(
        function_name="invoke_test",
        function_parameters={
            "param1": "value1-2viaproxy",
            "param2": "value2viaproxy"},
        time_out_in_sec=30)

    # Wait some time to be sure it has been processed and the system is
    # retrying delivery.
    time.sleep(5)

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address="tcp://*:51001",
        rpc_functions={
            "invoke_test": invoke_test},
        username="username2",
        password="password2")
    server_thread.start()

    # Wait some time to be sure it has been processed and the system is
    # retrying delivery. A retry cycle is max 1 sec.
    time.sleep(2)

    self.assertEquals(call_state.last_invoked_param1, "value1-2viaproxy")

    server_thread.stop()
    server_thread.join()
    buf_proxy_rep_req_thread.stop()
    buf_proxy_rep_req_thread.join()
    client.destroy()
    # Cleaning up sockets takes some time
    time.sleep(1)
