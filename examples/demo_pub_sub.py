

'''
Created on Apr 8, 2014
Edited on Oct 22, 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import sys
import time
from typing import Optional, Tuple

from zmqrpc import ZmqRpcClient, ZmqRpcServerThread


def test_method(param1, param2):
    print(
        'test_method invoked with params "{0}" and "{1}"'.format(
            param1,
            param2,
        )
    )


def main(args: Optional[Tuple[str]] = None) -> int:

    client = ZmqRpcClient(
        zmq_pub_endpoint='tcp://*:30000',
    )

    server = ZmqRpcServerThread(
        zmq_sub_connect_addresses=['tcp://localhost:30000'],    # Must be a list
        rpc_functions={             # Dict
            'test_method': test_method,
        },
    )

    server.start()

    # Wait a bit since sockets may not have been connected immediately
    time.sleep(2)

    client.invoke(
        function_name='test_method',
        function_parameters={  # Must be dict
            'param1': 'param1',
            'param2': 'param2',
        }
    )

    # Wait a bit to make sure message has been received
    time.sleep(2)

    # Clean up
    server.stop()
    server.join()

    return 0


if __name__ == '__main__':
    sys.exit(main())
