

import multiprocessing as mp
import signal
import sys
from time import sleep
from typing import Optional, Tuple

import zmq

_context = zmq.Context()
_tcp_end_point = 'tcp://127.0.0.1:65443'
_heart_beat = 'heartbeat'
_client_message = 'Hello'


class Server:

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

        print('Server received "%s"' % message)
        assert message == _client_message

        socket.send_string(_heart_beat)

    def run(self) -> None:
        print('Server running ..')

        self.__is_running = True

        while self.__is_running:
            self._handle_client()

    def stop(self) -> None:
        print('Server stopping ..')

        self.__is_running = False

        self.__socket.close()
        self.__socket = None


def _run_server(end_point: str) -> None:
    server = Server(end_point=end_point)

    server.run()


def _signal_handler(_, __) -> None:
    # Handle OS signals (like keyboard interrupt)
    print('Ctrl+C detected. Exiting...')
    sys.exit(0)


signal.signal(signal.SIGINT, _signal_handler)


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


def main(args: Optional[Tuple[str]] = None) -> int:

    end_point = _tcp_end_point

    print('using end point "%s"' % end_point)

    process = mp.Process(
        target=_run_server,
        args=(
            end_point,
        ),
        daemon=True,
    )
    process.start()

    for _ in range(3):
        sleep(2.0)

        client = Client(end_point=end_point)

        client.run()

        client.close()

    # Clean up
    process.terminate()

    print('exiting ...')

    return 0


if __name__ == '__main__':
    sys.exit(main())
