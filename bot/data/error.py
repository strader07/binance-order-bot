import json
from typing import List

from bot.commands import Command
from bot.data.adapters import Adapter
from bot.data.store import Store
from bot.orders.order import OrderTarget


class RawAdapter(Adapter):

    def to_raw(self, obj):
        return obj

    def from_raw(self, raw):
        return raw


class ErrorTracker(object):

    def __init__(self, failed_sell_orders: Store):
        self._failed_sell_orders = failed_sell_orders

    def failed_sell_order(self, command: Command, targets: List[OrderTarget], exceptions: List[Exception]):
        self._failed_sell_orders.store([command.symbol,
                                        OrderTarget.to_json(targets),
                                        command.source_name,
                                        command.type.value,
                                        self._exceptions_as_string(exceptions)])

    def _exceptions_as_string(self, exceptions: List[Exception]) -> str:
        return json.dumps([self._exception_as_string(ex) for ex in exceptions])

    def _exception_as_string(self, exception: Exception) -> str:
        pass
