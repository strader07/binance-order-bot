from abc import ABC, abstractmethod

from bot.commands import Command
from bot.commands.queue import CommandQueue
from bot.data.history import HistoryRecorder
from bot.orders.order import Order, OrderStatus, OrderType, OrderStatusType
from bot.orders.tracking.reporter import OrderCompletionReporter
from bot.orders.tracking.tracker import OrderTracker


class TrackedOrderHandler(ABC):

    @abstractmethod
    def can_handle(self, order: Order, status: OrderStatus) -> bool:
        pass

    @abstractmethod
    def handle(self, order: Order, status: OrderStatus) -> bool:
        pass


class DefaultHandler(TrackedOrderHandler):

    def can_handle(self, order: Order, status: OrderStatus) -> bool:
        return True

    def handle(self, order: Order, status: OrderStatus) -> bool:
        return False


class BuyOrderFilledHandler(TrackedOrderHandler):

    def __init__(self, command_queue: CommandQueue, history_recorder: HistoryRecorder):
        self._command_queue = command_queue
        self._history_recorder = history_recorder

    def can_handle(self, order: Order, status: OrderStatus) -> bool:
        return order.type == OrderType.BUY and status.is_filled

    def handle(self, order: Order, status: OrderStatus) -> bool:
        sell_command = Command(order.symbol,
                               order.targets,
                               OrderType.SELL,
                               order.source_name)
        self._command_queue.store(sell_command)

        self._history_recorder.record_order_completed(order)
        return True


class SellOrderFilledHandler(TrackedOrderHandler):

    def __init__(self, reporter: OrderCompletionReporter):
        self._reporter = reporter

    def can_handle(self, order: Order, status: OrderStatus) -> bool:
        return order.type == OrderType.SELL and status.is_filled

    def handle(self, order: Order, status: OrderStatus) -> bool:
        self._reporter.order_completed(order)
        return True


class SellOrderCanceledHandler(TrackedOrderHandler):

    def __init__(self, order_tracker: OrderTracker, history_recorder: HistoryRecorder):
        self._order_tracker = order_tracker
        self._history_recorder = history_recorder

    def can_handle(self, order: Order, status: OrderStatus) -> bool:
        return order.type == OrderType.SELL and status.type == OrderStatusType.CANCELED

    def handle(self, order: Order, status: OrderStatus) -> bool:
        with self._order_tracker.iterator() as iterator:
            item = iterator.next()
            while item is not None:
                if order.id == item.id:
                    iterator.delete()
                    break

                item = iterator.next()

        self._history_recorder.record_order_cancelled(order)
        return True
