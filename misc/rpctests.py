

'''
Created on Mar 31, 2014

@author: Jan Verhoeven

@copyright: MIT license, see http://opensource.org/licenses/MIT

'''


import logging
import time
import unittest

from zmqrpc.ZmqProxy import (
    ZmqBufferedProxyRep2ReqThread,
    ZmqProxyRep2PubThread,
    ZmqProxyRep2ReqThread,
    ZmqProxySub2PubThread,
    ZmqProxySub2ReqThread,
)
from zmqrpc.ZmqReceiver import ZmqReceiverThread
from zmqrpc.ZmqRpcClient import ZmqRpcClient
from zmqrpc.ZmqRpcServer import ZmqRpcServerThread
from zmqrpc.ZmqSender import ZmqSender

logger = logging.getLogger('zmqrpc')
logger.setLevel(logging.DEBUG)

# Track state from invoking method in a special class since this is in
# global scope.


class TestState(object):
    def __init__(self):
        self.last_invoked_param1 = None


test_state = TestState()


def invoke_test(param1, param2):
    test_state.last_invoked_param1 = param1
    return "{0}:{1}".format(param1, param2)


def invoke_test_that_throws_exception(param1, param2):
    del param1  # Unused
    del param2  # Unused
    raise Exception("Something went wrong")


class TestZmqPackage(unittest.TestCase):


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(name)s  %(message)s')
    logger = logging.getLogger("zmprpc")
    logger.setLevel(logging.DEBUG)
    unittest.main()
