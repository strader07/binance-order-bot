import logging

from bot.commands.queue import CommandQueue
from bot.data.history import HistoryRecorder
from bot.data.store import Store
from bot.orders.binance_api import Binance
from bot.orders.order import Order, OrderStatus
from bot.orders.tracking.handlers import DefaultHandler, BuyOrderFilledHandler, SellOrderFilledHandler, \
    SellOrderCanceledHandler
from bot.orders.tracking.reporter import OrderCompletionReporter
from bot.orders.tracking.tracker import OrderTracker


class OrderStatusHandler(object):

    def __init__(self, commands_queue: CommandQueue, reporter: OrderCompletionReporter,
                 order_tracker: OrderTracker, history_recorder: HistoryRecorder):
        self._all_handlers = [
            BuyOrderFilledHandler(commands_queue, history_recorder),
            SellOrderFilledHandler(reporter),
            SellOrderCanceledHandler(order_tracker, history_recorder)
        ]
        self._default_handler = DefaultHandler()

    def handle(self, order: Order, status: OrderStatus):
        for handler in self._all_handlers:
            if handler.can_handle(order, status):
                return handler.handle(order, status)

        return self._default_handler.handle(order, status)


class OrderTrackingTask(object):

    def __init__(self, order_tracker: OrderTracker, binance: Binance,
                 handler: OrderStatusHandler, logger: logging.Logger):
        self._order_tracker = order_tracker
        self._binance = binance
        self._handler = handler
        self._logger = logger

    def do_check(self):
        with self._order_tracker.iterator() as iterator:
            order = iterator.next()
            while order is not None:
                if self.check_order(order):
                    self._logger.debug('Deleting order data %s', order)
                    iterator.delete()

                order = iterator.next()

    def check_order(self, order: Order) -> bool:
        try:
            self._logger.debug('Checking order %s', order)

            status = self._binance.query_order_status(order)
            self._logger.info('Order %s status %s', order, status)

            return self._handler.handle(order, status)
        except Exception as e:
            self._logger.error('Order check error %s: %s', order, str(e))
            return False
