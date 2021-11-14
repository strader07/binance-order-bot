from bot.commands import Command
from bot.data.store import Store
from bot.orders.order import Order


class HistoryRecorder(object):

    def __init__(self, commands_store: Store, orders_store: Store,
                 order_completed: Store, order_cancelled: Store):
        self._commands_store = commands_store
        self._orders_store = orders_store
        self._order_completed = order_completed
        self._order_cancelled = order_cancelled

    def record_command(self, command: Command):
        self._commands_store.store(command)

    def record_order(self, order: Order):
        self._orders_store.store(order)

    def record_order_completed(self, order: Order):
        self._order_completed.store(order)

    def record_order_cancelled(self, order: Order):
        self._order_cancelled.store(order)
