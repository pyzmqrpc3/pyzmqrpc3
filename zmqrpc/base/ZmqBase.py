

from ..logger import logger


class ZmqBase:

    HEARTBEAT_MSG = 'zmq_sub_heartbeat'

    STATUS_CODE = 'status_code'
    STATUS_MSG = 'status_message'
    RESPONSE_MSG = 'response_message'

    STATUS_CODE_OK = 200
    STATUS_MSG_OK = 'OK'

    RPC_FUNCTION = 'function'
    RPC_PARAMETERS = 'parameters'

    STATUS_CODE_BAD_SERIALIZATION = 400
    STATUS_CODE_MISSING_FUNCTION = 450
    STATUS_CODE_BAD_FUNCTION = 451
    STATUS_CODE_EXCEPTION_RAISED = 463
    STATUS_CODE_PROXY_ERROR = 482

    def _debug(self, *args) -> None:
        logger.debug(*args)

    def _info(self, *args) -> None:
        logger.info(*args)

    def _warning(self, *args) -> None:
        logger.warning(*args)

    def _error(self, *args) -> None:
        logger.error(*args)

    def _exception(self, *args) -> None:
        logger.exception(*args)
