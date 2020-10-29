
# Testing

This package repository is running continuous integration using
[github actions](https://github.com/brgirgis/pyzmqrpc3/actions).
This ensures the integrity of the test suite and transparent code quality in
public.

## Test Suite

Tests are split into three files:

- `test_sockets`; which tests basic sender/receiver functionality
- `test_rpc.py`; which tests the RPC client/server functionality
- `test_proxy.py`; which tests proxy functionality with both sender/receiver
and RPC client/server

## Test Locally

To run the unit tests locally, install `pytest` package:

    pip install pytest

And from the root directory of the repository run:

    pytest

Make sure you do not run the unit tests in parallel because some of the tests
use the same sockets for testing purposes.

## VSCode Support

The repository also includes [VSCode](https://code.visualstudio.com/)
setup files to enable unit testing from inside the VSCode editor.
