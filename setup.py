

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
