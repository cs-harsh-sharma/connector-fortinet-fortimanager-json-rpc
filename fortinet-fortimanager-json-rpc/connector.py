"""
Copyright start
MIT License
Copyright (c) 2024 Fortinet Inc
Copyright end
"""

from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import _check_health, operations

logger = get_logger('fortinet-fortimanager-json-rpc')


class FortiManager(Connector):
    def execute(self, config, operation_name, params, **kwargs):
        try:
            op = operations.get(operation_name)
            result = op(config, params)
            return result
        except Exception as e:
            logger.exception("An exception occurred {}".format(e))
            raise ConnectorError(e)

    def check_health(self, config):
        try:
            _check_health(config)
            return True
        except Exception as e:
            logger.exception("An exception occurred in check_health {}".format(e))
            raise ConnectorError(e)
