from typing import List
from bot.orders.order import OrderTarget, OrderType


class Command(object):

    def __init__(self, symbol: str, targets: List[OrderTarget], type: OrderType, source_name: str, id: int = -1):
        self._symbol = symbol
        self._targets = targets
        self._type = type
        self._source_name = source_name
        self._id = id

    @property
    def id(self):
        return self._id

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def targets(self) -> List[OrderTarget]:
        return self._targets

    @property
    def type(self) -> OrderType:
        return self._type

    @property
    def source_name(self) -> str:
        return self._source_name

    def __eq__(self, other):
        return isinstance(other, Command) and \
               self.symbol == other.symbol and \
               self.targets == other.targets and \
               self.type == other.type and \
               self.source_name == other.source_name and \
               self.id == other.id

    def __repr__(self):
        return '[{}] {} ({}): {} ({})'\
            .format(self.id, self.source_name, self.type, self.symbol, self.targets)
