

'''
Created on Apr 2014
Edited on Oct 2020

@author: Jan Verhoeven
@author: Bassem Girgis

@copyright: MIT license, see http://opensource.org/licenses/MIT
'''


import argparse
import signal
import sys
from typing import Optional, Tuple

import zmq


# Handle OS signals (like keyboard interrupt)
def _signal_handler(_, __):
    print('Ctrl+C detected. Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)


def _get_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Reads and prints messages from a remote pub socket.'
    )

    parser.add_argument(
        '--sub',
        nargs='+',
        required=True,
        help='The PUB endpoint',
    )

    return parser.parse_args(args)


def main(args: Optional[Tuple[str]] = None) -> int:
    p_args = _get_args(args)
    print('Starting zmqsnoop...')

    try:
        context = zmq.Context()

        # Subscribe to all provided end-points
        sub_socket = context.socket(zmq.SUB)
        sub_socket.setsockopt(zmq.SUBSCRIBE, b'')
        for sub in p_args.sub:
            sub_socket.connect(sub)
            print('Connected to {0}'.format(sub))
        while True:
            # Process all parts of the message
            try:
                message_lines = sub_socket.recv_string().splitlines()
            except Exception as e:
                print('Error occurred with exception {0}'.format(e))
            for line in message_lines:
                print('>' + line)
    except Exception as e:
        print('Connection error {0}'.format(e))

    # Never gets here, but close anyway
    sub_socket.close()

    print('Exiting zmqsnoop...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
