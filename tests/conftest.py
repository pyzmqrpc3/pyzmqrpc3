
import logging
import sys
from functools import partial
from time import sleep

import pytest


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
