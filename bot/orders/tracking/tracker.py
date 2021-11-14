from bot.data.history import HistoryRecorder
from bot.data.store import Store
from bot.orders.order import Order

from bot.util.iterator import Iterator


class OrderTracker(Store):

    def __init__(self, store: Store, history_recorder: HistoryRecorder):
        self._store = store
        self._history_recorder = history_recorder

    def store(self, item: Order):
        self._store.store(item)
        self._history_recorder.record_order(item)

    def iterator(self) -> Iterator:
        return self._store.iterator()
