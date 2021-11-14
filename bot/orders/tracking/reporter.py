from bot.data.history import HistoryRecorder
from bot.data.store import Store
from bot.orders.order import Order


class OrderCompletionReporter(object):

    def __init__(self, store: Store, history_recorder: HistoryRecorder):
        self._store = store
        self._history_recorder = history_recorder

    def order_completed(self, order: Order):
        self._store.store(order)
        self._history_recorder.record_order_completed(order)
