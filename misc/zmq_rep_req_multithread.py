

import argparse
import signal
import sys
from threading import Thread
from time import sleep
from typing import Optional, Tuple

import zmq

_context = zmq.Context()
_inproc_end_point = 'inproc://hello'
_tcp_end_point = 'tcp://127.0.0.1:65443'
_heart_beat = 'heartbeat'
_client_message = 'Hello'


def _signal_handler(_, __) -> None:
    # Handle OS signals (like keyboard interrupt)
    print('Ctrl+C detected. Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)


class ServerThread(Thread):

    def __init__(self, end_point: str):
        super().__init__()

        self.__is_running = False
        self.__socket = socket = _context.socket(zmq.REP)
        socket.bind(end_point)

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, _, __) -> None:
        self.__is_running = False

    def _handle_client(self) -> None:
        socket = self.__socket

        try:
            message = socket.recv_string(zmq.NOBLOCK)
        except BaseException:
            return

        print('ServerThread received "%s"' % message)
        assert message == _client_message

        socket.send_string(_heart_beat)

    def run(self) -> None:
        print('ServerThread running ..')

        self.__is_running = True

        while self.__is_running:
            self._handle_client()

    def stop(self) -> None:
        print('ServerThread stopping ..')

        self.__is_running = False

        self.__socket.close()
        self.__socket = None


class Client:

    def __init__(self, end_point: str):
        self.__socket = socket = _context.socket(zmq.REQ)
        socket.connect(end_point)

        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, _, __) -> None:
        self.close()

    def close(self) -> None:
        print('Client stopping ..')
        self.__socket.close()

    def run(self) -> None:
        socket = self.__socket

        print('Client waiting for response ...')

        socket.send_string(_client_message)

        response = socket.recv_string()

        print('Client received "%s"' % response)
        assert response == _heart_beat


def _get_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='run a simple Server/Client example using multithreads.'
    )

    parser.add_argument(
        '--use_tcp',
        action='store_true',
        help='use tcp communication instead of inproc'
    )

    return parser.parse_args(args)


def main(args: Optional[Tuple[str]] = None) -> int:
    p_args = _get_args(args)

    end_point = _tcp_end_point if p_args.use_tcp else _inproc_end_point

    print('using end point "%s"' % end_point)

    server = ServerThread(end_point=end_point)
    server.start()

    for _ in range(3):
        sleep(2.0)

        client = Client(end_point=end_point)

        client.run()

        client.close()

    # Clean up
    server.stop()
    server.join()

    print('exiting ...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
