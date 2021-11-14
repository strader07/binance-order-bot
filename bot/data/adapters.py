from abc import ABC, abstractmethod
from typing import List

from bot.commands import Command
from bot.orders.order import OrderTarget, Order, OrderType


class Adapter(ABC):

    @abstractmethod
    def to_raw(self, obj):
        pass

    @abstractmethod
    def from_raw(self, raw):
        pass


class OrderToSheetRowAdpater(Adapter):

    def to_raw(self, obj: Order):
        return [obj.id,
                OrderTarget.to_json(obj.targets),
                obj.source_name,
                obj.symbol,
                obj.type.value]

    def from_raw(self, raw: List):
        order_id = raw[0]
        targets = OrderTarget.from_json(raw[1])
        source_name = raw[2]
        symbol = raw[3]
        order_type = OrderType.from_value(raw[4])
        return Order(order_id, symbol, targets, order_type, source_name)


class CommandToSheetRowAdapter(Adapter):

    def to_raw(self, obj: Command):
        return [obj.symbol,
                OrderTarget.to_json(obj.targets),
                obj.source_name,
                obj.type.value,
                obj.id]

    def from_raw(self, raw: List):
        symbol = raw[0]
        targets = OrderTarget.from_json(raw[1])
        source_name = raw[2]
        order_type = OrderType.from_value(raw[3])
        id = int(raw[4])
        return Command(symbol, targets, order_type, source_name, id)
