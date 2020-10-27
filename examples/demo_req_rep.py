

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import sys
import time
from typing import Optional, Tuple

from zmqrpc import ZmqRpcClient, ZmqRpcServerThread


def test_method(param1, param2) -> str:
    print(
        'test_method invoked with params "{0}" and "{1}"'.format(
            param1,
            param2,
        )
    )
    return 'test_method response text for argument %s' % str(
        dict(param1=param1, param2=param2)
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
        rpc_functions={             # Dict
            'test_method': test_method,
        },
        username='test',
        password='test',
    )
    server.start()

    # Wait a bit since sockets may not have been connected immediately
    time.sleep(2)

    # REQ/REQ sockets can carry a response
    response = client.invoke(
        function_name='test_method',
        function_parameters={  # Must be dict
            'param1': 'passed param1',
            'param2': 'passed param2',
        },
    )

    print('response: {0}'.format(response))

    # Wait a bit to make sure message has been received
    time.sleep(2)

    # Clean up
    server.stop()
    server.join()

    return 0


if __name__ == '__main__':
    sys.exit(main())
