

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from functools import partial

from zmqrpc import ZmqRpcClient, ZmqRpcServerThread


def test_rpc1_req_rep(logger, close_socket_delay, call_state, invoke_callback):
    # RPC invoke method over REQ/REP sockets
    logger.info(
        'Test if invoking a method works over REQ/REP RPC socket, '
        'includes a username/password'
    )

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        rpc_functions={
            'invoke_test': partial(invoke_callback, call_state),
        },
        username='username',
        password='password',
    )
    server_thread.start()

    response = client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'value1',
            'param2': 'value2',
        },
        time_out_in_sec=3,
    )

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert response[0] == 'value1:value2'
    assert call_state.last_invoked_param1 == 'value1'


def test_rpc1_req_rep_invalid_function(
        logger,
        close_socket_delay,
        call_state,
        invoke_callback):
    # RPC invoke method over REQ/REP sockets
    logger.info(
        'Test if invoking a non existing method throws proper '
        'error over REQ/REP RPC socket, includes a username/password'
    )
    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        rpc_functions={
            'invoke_test': partial(invoke_callback, call_state),
        },
        username='username',
        password='password',
    )
    server_thread.start()

    try:
        client.invoke(
            function_name='invoke_test_does_not_exist',
            function_parameters={
                'param1': 'value1',
                'param2': 'value2',
            },
            time_out_in_sec=3,
        )
    except Exception as e:
        assert str(e) == 'Function "invoke_test_does_not_exist" is not ' \
            'implemented on server. Check rpc_functions on server if it ' \
            'contains the function name'
        assert call_state.last_invoked_param1 is None

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_rpc1_req_rep_exception_raised(
        logger,
        close_socket_delay,
        call_state,
        invoke_callback_exception):
    # RPC invoke method over REQ/REP sockets
    logger.info(
        'Test if invoking an existing method that throws an'
        ' exception over REQ/REP RPC socket, includes a username/password'
    )

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        rpc_functions={
            'invoke_test_with_exception': partial(
                invoke_callback_exception,
                call_state,
            ),
        },
        username='username',
        password='password',
    )
    server_thread.start()

    try:
        client.invoke(
            function_name='invoke_test_with_exception',
            function_parameters={
                'param1': 'value1',
                'param2': 'value2',
            },
            time_out_in_sec=3,
        )
    except Exception as e:
        assert str(e) == 'Exception raised when calling function ' \
            'invoke_test_with_exception. Exception: Something went wrong '
        assert call_state.last_invoked_param1 == 'Exception Raised'

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_rpc1_pub_sub(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay,
        call_state,
        invoke_callback):
    # RPC invoke method over REQ/REP sockets
    logger.info('Test if invoking a method works over PUB/SUB RPC socket')

    client = ZmqRpcClient(zmq_pub_endpoint='tcp://*:54000')

    server_thread = ZmqRpcServerThread(
        zmq_sub_connect_addresses=['tcp://localhost:54000'],
        rpc_functions={
            'invoke_test': partial(invoke_callback, call_state),
        },
        username='username',
        password='password',
    )
    server_thread.start()

    # Wait a bit to avoid slow joiner...
    slow_joiner_delay()

    response = client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'value1sub',
            'param2': 'value2pub',
        },
        time_out_in_sec=3,
    )

    # Wait a bit to make sure message is sent...
    two_sec_delay()

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    # Response should be empty with PUB/SUB
    assert response is None
    assert call_state.last_invoked_param1 == 'value1sub'


def test_pub_sub_timeout_per_socket_using_heartbeat_function(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay,
        call_state,
        invoke_callback):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test a timeout per socket with RPC using heartbeat')

    client = ZmqRpcClient(zmq_pub_endpoint='tcp://*:47001')

    server_thread = ZmqRpcServerThread(
        zmq_sub_connect_addresses=[
            (
                'tcp://localhost:47001',
                3,
            ),
        ],
        rpc_functions={
            'invoke_test': partial(invoke_callback, call_state),
        },
        recreate_timeout=10,
    )
    server_thread.start()

    # Slow joiner
    slow_joiner_delay()

    first_socket = server_thread.get_sub_socket(idx=0).zmq_socket

    client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'testxx-value1',
            'param2': 'value2',
        },
        time_out_in_sec=3,
    )

    # Take 2 seconds to see if it works in case of within the 3 seconds
    # window.
    two_sec_delay()

    assert call_state.last_invoked_param1 == 'testxx-value1'

    # Now send another but with 2 seconds delay, which should be ok, then
    # followed by a couple of heartbeats which should keep the existing
    # socket.
    client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'testxx-value2',
            'param2': 'value2',
        },
        time_out_in_sec=3,
    )

    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    assert call_state.last_invoked_param1 == 'testxx-value2'
    assert server_thread.get_sub_socket(idx=0).zmq_socket == first_socket

    # Now send another but with 4 seconds delay, which should restart the
    # sockets, but message should arrive
    client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'testxx-value3',
            'param2': 'value2',
        },
        time_out_in_sec=3,
    )

    two_sec_delay()
    two_sec_delay()

    assert call_state.last_invoked_param1 == 'testxx-value3'
    second_socket = server_thread.get_sub_socket(idx=0).zmq_socket
    assert second_socket != first_socket

    # Now send another but with 2 seconds delay, which should be ok
    client.invoke(
        function_name='invoke_test',
        function_parameters={
            'param1': 'testxx-value4',
            'param2': 'value2',
        },
        time_out_in_sec=3,
    )

    two_sec_delay()

    assert server_thread.get_sub_socket(idx=0).zmq_socket == second_socket

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert call_state.last_invoked_param1 == 'testxx-value4'
