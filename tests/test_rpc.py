

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from zmqrpc import ICommand, ShutdownServer, ZmqRpcClient, ZmqRpcServerThread

from .Command import Command
from .InvalidCommandConstructor import InvalidCommandConstructor
from .Service import Service
from .ServiceWithException import ServiceWithException
from .State import State


def test_valid_rpc_registration(logger, close_socket_delay):
    logger.info(
        'Test if invalid registrations raise errors'
    )

    call_state = State()

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        username='username',
        password='password',
    )

    is_success = None
    try:
        server_thread.register_service(
            command_class=ICommand,
            service=Service(state=call_state),
        )
        is_success = False
        logger.error(
            'Cannot register a service for ICommand'
        )
    except BaseException:
        is_success = True

    assert is_success

    is_success = None
    try:
        server_thread.register_service(
            command_class=Service,
            service=Service(state=call_state),
        )
        is_success = False
        logger.error(
            'Command has to inherit from ICommand'
        )
    except BaseException:
        is_success = True

    assert is_success

    is_success = None
    try:
        server_thread.register_service(
            command_class=InvalidCommandConstructor,
            service=Service(state=call_state),
        )
        is_success = False
        logger.error(
            'Command needs to have a default constructor'
        )
    except BaseException:
        is_success = True

    assert is_success

    is_success = None
    try:
        server_thread.register_service(
            command_class=Command,
            service=Command(),
        )
        is_success = False
        logger.error(
            'Service needs to inherit from IService'
        )
    except BaseException:
        is_success = True

    assert is_success

    server_thread.start()

    server_thread.stop()
    server_thread.join()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_rpc_shutdown_server(logger, close_socket_delay):
    logger.info(
        'Test if we can shutdown the server from the client'
    )

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        username='username',
        password='password',
    )
    server_thread.start()

    client.execute_remote(
        command=ShutdownServer(),
        time_out_in_sec=3,
    )

    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert not server_thread.is_alive()
    assert not server_thread.is_running


def test_rpc1_req_rep(logger, close_socket_delay):
    logger.info(
        'Test if executing a command works over REQ/REP RPC socket, '
        'includes a username/password'
    )

    call_state = State()

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        username='username',
        password='password',
    )
    server_thread.register_service(
        command_class=Command,
        service=Service(state=call_state),
    )
    server_thread.start()

    response = client.execute_remote(
        command=Command(param1='value1', param2='value2'),
        time_out_in_sec=3,
    )

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert response[0] == 'value1:value2'
    assert call_state.last_param1 == 'value1'


def test_rpc1_req_rep_invalid_command(logger, close_socket_delay):
    logger.info(
        'Test if executing a non existing command throws proper '
        'error over REQ/REP RPC socket, includes a username/password'
    )

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        username='username',
        password='password',
    )
    server_thread.start()

    try:
        client.execute_remote(
            command=Command(param1='value1', param2='value2'),
            time_out_in_sec=3,
        )
    except Exception as e:
        assert str(e) == 'No service on the server is registered for ' \
            'command "Command".'

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_rpc1_req_rep_exception_raised(logger, close_socket_delay):
    logger.info(
        'Test if executing a command that throws an'
        ' exception over REQ/REP RPC socket, includes a username/password'
    )

    call_state = State()

    client = ZmqRpcClient(
        zmq_req_endpoints=['tcp://localhost:55000'],
        username='username',
        password='password',
    )

    server_thread = ZmqRpcServerThread(
        zmq_rep_bind_address='tcp://*:55000',
        username='username',
        password='password',
    )
    server_thread.register_service(
        command_class=Command,
        service=ServiceWithException(state=call_state),
    )
    server_thread.start()

    try:
        client.execute_remote(
            command=Command(param1='value1', param2='value2'),
            time_out_in_sec=3,
        )
    except Exception as e:
        assert str(e) == 'Exception raised when calling service ' \
            'ServiceWithException. Exception: Something went wrong '
        assert call_state.last_param1 == 'Exception Raised'

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_rpc1_pub_sub(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    logger.info('Test if executing a command works over PUB/SUB RPC socket')

    call_state = State()

    client = ZmqRpcClient(zmq_pub_endpoint='tcp://*:54000')

    server_thread = ZmqRpcServerThread(
        zmq_sub_connect_addresses=['tcp://localhost:54000'],
        username='username',
        password='password',
    )
    server_thread.register_service(
        command_class=Command,
        service=Service(state=call_state),
    )
    server_thread.start()

    # Wait a bit to avoid slow joiner...
    slow_joiner_delay()

    response = client.execute_remote(
        command=Command(param1='value1sub', param2='value2pub'),
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
    assert call_state.last_param1 == 'value1sub'


def test_pub_sub_timeout_per_socket_using_heartbeat_function(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test a timeout per socket with RPC using heartbeat')

    call_state = State()

    client = ZmqRpcClient(zmq_pub_endpoint='tcp://*:47001')

    server_thread = ZmqRpcServerThread(
        zmq_sub_connect_addresses=[
            (
                'tcp://localhost:47001',
                3,
            ),
        ],
        recreate_timeout=10,
    )
    server_thread.register_service(
        command_class=Command,
        service=Service(state=call_state),
    )
    server_thread.start()

    # Slow joiner
    slow_joiner_delay()

    first_socket = server_thread.get_sub_socket(idx=0).zmq_socket

    client.execute_remote(
        command=Command(param1='testxx-value1', param2='value2'),
        time_out_in_sec=3,
    )

    # Take 2 seconds to see if it works in case of within the 3 seconds
    # window.
    two_sec_delay()

    assert call_state.last_param1 == 'testxx-value1'

    # Now send another but with 2 seconds delay, which should be ok, then
    # followed by a couple of heartbeats which should keep the existing
    # socket.
    client.execute_remote(
        command=Command(param1='testxx-value2', param2='value2'),
        time_out_in_sec=3,
    )

    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    client.send_heartbeat()
    two_sec_delay()

    assert call_state.last_param1 == 'testxx-value2'
    assert server_thread.get_sub_socket(idx=0).zmq_socket == first_socket

    # Now send another but with 4 seconds delay, which should restart the
    # sockets, but message should arrive
    client.execute_remote(
        command=Command(param1='testxx-value3', param2='value2'),
        time_out_in_sec=3,
    )

    two_sec_delay()
    two_sec_delay()

    assert call_state.last_param1 == 'testxx-value3'
    second_socket = server_thread.get_sub_socket(idx=0).zmq_socket
    assert second_socket != first_socket

    # Now send another but with 2 seconds delay, which should be ok
    client.execute_remote(
        command=Command(param1='testxx-value4', param2='value2'),
        time_out_in_sec=3,
    )

    two_sec_delay()

    assert server_thread.get_sub_socket(idx=0).zmq_socket == second_socket

    server_thread.stop()
    server_thread.join()
    client.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert call_state.last_param1 == 'testxx-value4'
