

from setuptools import setup

name = 'pyamqrpc3'

description = 'A simple ZMQ RPC extension with JSON for message serialization'

long_description = \
    """
The `pyreadline3` package is based on the stale package `pyreadline` located
at https://github.com/pyreadline/pyreadline.
The original `pyreadline` package is a python implementation of GNU `readline`
functionality.
It is based on the `ctypes` based UNC `readline` package by Gary Bishop.
It is not complete.
It has been tested for use with Windows 10.

Version 3.0+ or pyreadline3 runs on Python 3.3+.

Features

- keyboard text selection and copy/paste
- Shift-arrowkeys for text selection
- Control-c can be used for copy activate with allow_ctrl_c(True) in config file
- Double tapping ctrl-c will raise a KeyboardInterrupt, use ctrl_c_tap_time_interval(x)
- where x is your preferred tap time window, default 0.3 s.
- paste pastes first line of content on clipboard.
- ipython_paste, pastes tab-separated data as list of lists or numpy array if all data is numeric
- paste_mulitline_code pastes multi line code, removing any empty lines.

The latest development version is always available at the project git
repository https://github.com/brgirgis/pyreadline3
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

license_name = 'MIT'

install_requires = [
    "pyzmq>=15.0.0",
    "future>=0.15.0",
]

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
