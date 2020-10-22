

import os
from typing import List

from setuptools import setup

_dir = os.path.dirname(__file__)

_init_path = os.path.join(_dir, 'zmqrpc', '__init__.py')
_req_path = os.path.join(_dir, 'requirements.txt')


def _get_version() -> str:
    for line in open(_init_path, 'r').readlines():
        if 'version_info' not in line:
            continue
        ver_tuple_str = line.split('=')[1].replace('(', '').replace(')', '')
        return '.'.join(
            tuple(
                x.strip()
                for x in ver_tuple_str.split(',')
            )
        )


def _get_requirements() -> List[str]:
    return [
        line.strip()
        for line in open(_req_path, 'r').readlines()
    ]


name = 'pyamqrpc3'

description = 'A simple ZMQ RPC extension with JSON for message serialization'

long_description = \
    """
This Python package adds basic Remote Procedure Call functionalities to ZeroMQ.
It does not do advanced serializing, but simply uses JSON call and
response structures.

To Install:

pip install pyzmqrpc3

Usage:

Implement a function on the server that can be invoked:

    def test_method(param1, param2):
        return param1 + param2

Create a ZeroMQ server:

    server = ZmqRpcServerThread(zmq_rep_bind_address="tcp://*:30000",
            rpc_functions={"test_method": test_method})
    server.start()

Create a client that connects to that server endpoint:

    client = ZmqRpcClient(zmq_req_endpoints=["tcp://localhost:30000"])

Have the client invoke the function on the server:

    client.invoke(function_name="test_method",
            function_parameters={"param1": "Hello", "param2": " world"})

The latest development version and more examples below and are included in
project repository https://github.com/brgirgis/pyzmqrpc3
"""

authors = {
    'Bassem': ('Bassem Girgis', 'brgirgis@gmail.com'),
    'Jorgen': ('Jan Verhoeven', 'jan@captive.nl'),
}

url = 'https://github.com/brgirgis/pyzmqrpc3'

download_url = 'https://pypi.org/project/pyzmqrpc3/'

keywords = [
    'zmq',
    'zeromq',
    'pyzmq',
    'rpc',
]

version = _get_version()
install_requires = _get_requirements()

license_name = 'MIT'

packages = [
    'zmqrpc',
    'zmqrpc.client',
    'zmqrpc.proxy',
    'zmqrpc.receiver',
    'zmqrpc.sender',
    'zmqrpc.server',
]

setup(
    name=name,
    version=version,
    description=description,
    long_description=long_description,
    author=authors["Bassem"][0],
    author_email=authors["Bassem"][1],
    maintainer=authors["Bassem"][0],
    maintainer_email=authors["Bassem"][1],
    license=license_name,
    url=url,
    download_url=download_url,
    keywords=keywords,
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
)
