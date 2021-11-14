from typing import List
from datetime import datetime

import enum
import json


class OrderTarget(object):

    def __init__(self, price_end, qty_percentage):
        self._price_end = price_end
        self._qty_percentage = qty_percentage

    @property
    def price_end(self) -> int:
        return self._price_end

    @property
    def qty_percentage(self) -> float:
        return self._qty_percentage

    def __eq__(self, other):
        return isinstance(other, OrderTarget) and \
               self.price_end == other.price_end and \
               self.qty_percentage == other.qty_percentage

    def __repr__(self):
        return '{} {}'.format(self.price_end, self.qty_percentage)

    @staticmethod
    def to_json(targets: List['OrderTarget']):
        return json.dumps([[t.price_end, t.qty_percentage] for t in targets])

    @staticmethod
    def from_json(targets: str) -> List['OrderTarget']:
        return [OrderTarget(int(t[0]), float(t[1])) for t in json.loads(targets)]


class OrderType(enum.Enum):
    BUY = 'buy'
    SELL = 'sell'

    @staticmethod
    def from_value(value: str) -> 'OrderType':
        return OrderType(value)


class OrderStatusType(enum.Enum):
    NEW = 'NEW'
    PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    FILLED = 'FILLED'
    CANCELED = 'CANCELED'
    PENDING_CANCEL = 'PENDING_CANCEL'
    REJECTED = 'REJECTED'
    EXPIRED = 'EXPIRED'

    @staticmethod
    def from_value(value: str) -> 'OrderStatusType':
        return OrderStatusType(value)


class Order(object):

    def __init__(self, order_id, symbol, targets, type, source_name):
        self._order_id = order_id
        self._symbol = symbol
        self._targets = targets
        self._type = type
        self._source_name = source_name

    @property
    def id(self) -> str:
        return self._order_id

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
        return isinstance(other, Order) and \
               self.id == other.id and \
               self.symbol == other.symbol and \
               self.targets == other.targets and \
               self.type == other.type and \
               self.source_name == other.source_name

    def __repr__(self):
        return '{} ({}, {}): {} ({})'\
            .format(self.source_name, self.id, self.type, self.symbol, self.targets)


class OrderStatus(object):

    def __init__(self, status: OrderStatusType, last_update_time: int):
        self._status = status
        self._last_update_time = datetime.fromtimestamp(last_update_time * 0.001)

    @property
    def type(self) -> OrderStatusType:
        return self._status

    @property
    def is_filled(self) -> bool:
        return self._status == OrderStatusType.FILLED

    @property
    def update_time(self) -> datetime:
        return self._last_update_time

    def __repr__(self):
        return '{}: {}'.format(self.update_time, self.type)
