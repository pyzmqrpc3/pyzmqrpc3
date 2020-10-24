

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


from zmqrpc import ZmqReceiverThread, ZmqSender


def test_req_rep_sockets(logger, close_socket_delay):
    # Basic send/receive over REQ/REP sockets
    logger.info(
        'Test if sending works over REQ/REP socket, '
        'includes a username/password'
    )

    sender = ZmqSender(
        zmq_req_endpoints=['tcp://localhost:47000'],
        username='username',
        password='password',
    )

    receiver_thread = ZmqReceiverThread(
        zmq_rep_bind_address='tcp://*:47000',
        username='username',
        password='password',
    )

    receiver_thread.start()

    sender.send('test', time_out_in_sec=3)

    assert receiver_thread.get_last_received_message() == 'test'

    logger.info(
        'Test if sending wrong password over REP/REQ connection '
        'results in error (actually timeout)'
    )

    sender = ZmqSender(
        zmq_req_endpoints=['tcp://localhost:47000'],
        username='username',
        password='wrongpassword',
    )

    is_success = True
    try:
        sender.send('test', time_out_in_sec=3)
        logger.info(
            'Error. Did get answer from remote system which was not expected')
        is_success = False
    except BaseException:
        # Could not send message, which is ok in this case
        logger.info('Success.')

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert is_success


def test_req_rep_sockets_over_inproc(logger, close_socket_delay):
    # Basic send/receive over REQ/REP sockets
    logger.info(
        'Test if sending works over REQ/REP socket using inproc, '
        'includes a username/password'
    )

    sender = ZmqSender(
        zmq_req_endpoints=['inproc://test'],
        username='username',
        password='password',
    )

    receiver_thread = ZmqReceiverThread(
        zmq_rep_bind_address='inproc://test',
        username='username',
        password='password',
    )
    receiver_thread.start()

    sender.send('test', time_out_in_sec=3)

    assert receiver_thread.get_last_received_message() == 'test'

    logger.info(
        'Test if sending wrong password over REP/REQ connection '
        'results in error (actually timeout)'
    )

    sender = ZmqSender(
        zmq_req_endpoints=['inproc://test'],
        username='username',
        password='wrongpassword',
    )

    is_success = True
    try:
        logger.error(
            'Error. Did get answer from remote system which was not expected')
        is_success = False
    except BaseException:
        # Could not send message, which is ok in this case
        logger.info('Success.')

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()

    assert is_success


def test_pub_sub_without_passwords(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test if sending works over PUB/SUB sockets without passwords')

    sender = ZmqSender(zmq_pub_endpoint='tcp://*:47001')

    receiver_thread = ZmqReceiverThread(
        zmq_sub_connect_addresses=['tcp://localhost:47001'])
    receiver_thread.start()

    # Take 0.5 second for sockets to connect to prevent 'slow joiner'
    # problem
    slow_joiner_delay()

    sender.send('test')

    # Sleep for pub/sub not guaranteed to be done on completing
    # send_pub_socket
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test'

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_pub_sub_without_passwords_over_inproc(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test if sending works over PUB/SUB sockets without passwords')

    sender = ZmqSender(zmq_pub_endpoint='inproc://my_test')

    receiver_thread = ZmqReceiverThread(
        zmq_sub_connect_addresses=['inproc://my_test'],
    )
    receiver_thread.start()

    # Take 0.5 second for sockets to connect to prevent 'slow joiner'
    # problem
    slow_joiner_delay()

    sender.send('test')

    # Sleep for pub/sub not guaranteed to be done on completing
    # send_pub_socket
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test'

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_pub_sub_timeout(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test a timeout')

    sender = ZmqSender(zmq_pub_endpoint='tcp://*:47001')

    receiver_thread = ZmqReceiverThread(
        zmq_sub_connect_addresses=['tcp://localhost:47001'],
        recreate_timeout=3,
    )
    receiver_thread.start()

    # Slow joiner
    slow_joiner_delay()

    first_socket = receiver_thread.get_sub_socket(idx=0).zmq_socket
    sender.send('test')

    # Take 2 seconds to see if it works in case of within the 3 seconds
    # window.
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test'

    # Now send another but with 2 seconds delay, which should be ok
    sender.send('test2')
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test2'
    assert receiver_thread.get_sub_socket(idx=0).zmq_socket == first_socket

    # Now send another but with 4 seconds delay, which should restart the
    # sockets, but message should arrive
    sender.send('test3')
    two_sec_delay()
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test3'
    second_socket = receiver_thread.get_sub_socket(idx=0).zmq_socket
    assert second_socket != first_socket

    # Now send another but with 2 seconds delay, which should be ok
    sender.send('test4')
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test4'
    assert receiver_thread.get_sub_socket(idx=0).zmq_socket == second_socket

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()


def test_pub_sub_timeout_per_socket(
        logger,
        close_socket_delay,
        slow_joiner_delay,
        two_sec_delay):
    # Basic send/receive over PUB/SUB sockets
    logger.info('Test a timeout per socket')

    sender = ZmqSender(zmq_pub_endpoint='tcp://*:47001')

    receiver_thread = ZmqReceiverThread(
        zmq_sub_connect_addresses=[
            ('tcp://localhost:47001', 3),
        ],
        recreate_timeout=10,
    )
    receiver_thread.start()

    # Slow joiner
    slow_joiner_delay()

    first_socket = receiver_thread.get_sub_socket(idx=0).zmq_socket
    sender.send('test')
    # Take 2 seconds to see if it works in case of within the 3 seconds
    # window.
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test'

    # Now send another but with 2 seconds delay, which should be ok,
    # followed by 4 heartbeats. Socket should not be refreshed.
    sender.send('test2')
    two_sec_delay()

    sender.send_heartbeat()
    two_sec_delay()

    sender.send_heartbeat()
    two_sec_delay()

    sender.send_heartbeat()
    two_sec_delay()

    sender.send_heartbeat()

    assert receiver_thread.get_last_received_message() == 'test2'
    assert receiver_thread.get_sub_socket(idx=0).zmq_socket == first_socket

    # Now send another but with 4 seconds delay, which should restart the
    # sockets, but message should arrive
    sender.send('test3')
    two_sec_delay()
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test3'
    second_socket = receiver_thread.get_sub_socket(idx=0).zmq_socket
    assert second_socket != first_socket

    # Now send another but with 2 seconds delay, which should be ok
    sender.send('test4')
    two_sec_delay()

    assert receiver_thread.get_last_received_message() == 'test4'
    assert receiver_thread.get_sub_socket(idx=0).zmq_socket == second_socket

    receiver_thread.stop()
    receiver_thread.join()
    sender.destroy()

    # Cleaning up sockets takes some time
    close_socket_delay()
