
import logging
import sys
from functools import partial
from time import sleep

import pytest

from .State import State


@pytest.fixture(scope='package')
def logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s] %(message)s'
    )
    handler.setFormatter(formatter)

    root.addHandler(handler)

    _logger = logging.getLogger('zmqrpc')
    _logger.setLevel(logging.DEBUG)
    return _logger


@pytest.fixture(scope='package')
def close_socket_delay():
    return partial(sleep, 1)


@pytest.fixture(scope='package')
def slow_joiner_delay():
    return partial(sleep, 0.5)


@pytest.fixture(scope='package')
def two_sec_delay():
    return partial(sleep, 2)


@pytest.fixture(scope='function')
def call_state():
    return State()


@pytest.fixture(scope='function')
def invoke_callback():
    def _invoke_test(state: State, param1, param2):
        state.last_invoked_param1 = param1
        return '{0}:{1}'.format(param1, param2)
    return _invoke_test


@pytest.fixture(scope='function')
def invoke_callback_exception():
    def _invoke_test(state: State, param1, param2):
        del param1  # Unused
        del param2  # Unused
        state.last_invoked_param1 = 'Exception Raised'
        raise Exception('Something went wrong')
    return _invoke_test
