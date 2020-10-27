

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

from zmqrpc import (
    ZmqProxyRep2Pub,
    ZmqProxyRep2Req,
    ZmqProxySub2Pub,
    ZmqProxySub2Req,
)


# Handle OS signals (like keyboard interrupt)
def _signal_handler(_, __):
    print('Ctrl+C detected. Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)


def _get_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Proxies message either from SUB->REQ, '
        'SUB->PUB, REP->PUB or REP->REQ.', )

    parser.add_argument(
        '--sub',
        nargs='+',
        required=False,
        help='The SUB endpoints',
    )

    parser.add_argument('--pub', required=False, help='The PUB endpoint')

    parser.add_argument(
        '--req',
        nargs='+',
        required=False,
        help='The REQ endpoint',
    )

    parser.add_argument('--rep', required=False, help='The REP endpoint')

    parser.add_argument(
        '--username_incoming',
        required=False,
        help='In case a username is needed for the incoming '
        'connection (sub, rep)',
    )

    parser.add_argument(
        '--password_incoming',
        required=False,
        help='In case a password is needed for the incoming '
        'connection (sub, rep)',
    )

    parser.add_argument(
        '--username_outgoing',
        required=False,
        help='In case a username is needed for the outgoing '
        'connection (req, pub)',
    )

    parser.add_argument(
        '--password_outgoing',
        required=False,
        help='In case a password is needed for the outgoing '
        'connection (req, pub)',
    )

    return parser.parse_args(args)


def main(args: Optional[Tuple[str]] = None) -> int:
    p_args = _get_args(args)

    if p_args.sub is not None and p_args.rep is not None:
        print(
            'Fatal error: Proxy cannot listen to both SUB and REP at '
            'the same time'
        )
        return 1

    if p_args.pub is not None and p_args.req is not None:
        print(
            'Fatal error: Proxy cannot send messages over both PUB '
            'and REQ sockets at the same time'
        )
        return 1

    if (p_args.sub is not None or p_args.rep is not None) and (
            p_args.pub is not None or p_args.req is not None):
        print('Starting zmqproxy...')

        if p_args.sub is not None and p_args.req is not None:
            server = ZmqProxySub2Req(
                zmq_sub_connect_addresses=p_args.sub,
                zmq_req_connect_addresses=p_args.req,
                username_sub=p_args.username_incoming,
                password_sub=p_args.password_incoming,
                username_req=p_args.username_outgoing,
                password_req=p_args.password_outgoing,
            )
        elif p_args.rep is not None and p_args.pub is not None:
            server = ZmqProxyRep2Pub(
                zmq_rep_bind_address=p_args.rep,
                zmq_pub_bind_address=p_args.pub,
                username_rep=p_args.username_incoming,
                password_rep=p_args.password_incoming,
                username_pub=p_args.username_outgoing,
                password_pub=p_args.password_outgoing,
            )
        elif p_args.sub is not None and p_args.pub is not None:
            server = ZmqProxySub2Pub(
                zmq_sub_connect_addresses=p_args.sub,
                zmq_pub_bind_address=p_args.pub,
                username_sub=p_args.username_incoming,
                password_sub=p_args.password_incoming,
                username_pub=p_args.username_outgoing,
                password_pub=p_args.password_outgoing,
            )
        elif p_args.rep is not None and p_args.req is not None:
            server = ZmqProxyRep2Req(
                zmq_rep_bind_address=p_args.rep,
                zmq_req_connect_addresses=p_args.req,
                username_rep=p_args.username_incoming,
                password_rep=p_args.password_incoming,
                username_req=p_args.username_outgoing,
                password_req=p_args.password_outgoing,
            )

        server.run()

        print('Stopped zmqproxy...')

        return 0

    return 1


if __name__ == '__main__':
    sys.exit(main())
