import logging
from abc import ABC, abstractmethod

from bot.commands.command import Command
from bot.commands.factory import CommandFactory
from bot.data.history import HistoryRecorder
from bot.data.store import Store

from bot.util.iterator import Iterator


class CommandHandler(ABC):

    @abstractmethod
    def can_handle(self, command: Command) -> bool:
        pass

    @abstractmethod
    def handle(self, command: Command):
        pass


class CommandQueue(Store):

    def __init__(self, store: Store, history_recorder: HistoryRecorder, factory: CommandFactory):
        self._store = store
        self._history_recorder = history_recorder
        self._factory = factory

    def store(self, item: Command):
        item = self._factory.create_from(item)

        self._store.store(item)
        self._history_recorder.record_command(item)

    def iterator(self) -> Iterator:
        return self._store.iterator()


class CommandQueueProcessor(object):

    def __init__(self, queue: CommandQueue, handler: CommandHandler, logger: logging.Logger):
        self._queue = queue
        self._handler = handler
        self._logger = logger

    def process_all(self):
        with self._queue.iterator() as iterator:
            command = iterator.next()
            while command is not None:
                if self.process(command):
                    self._logger.debug('Deleting command %s', command)
                    iterator.delete()

                command = iterator.next()

    def process(self, command: Command) -> bool:
        try:
            self._logger.info('Processing command %s', command)

            if not self._handler.can_handle(command):
                self._logger.warning('Cannot handle command %s')
                return False

            self._handler.handle(command)
            self._logger.debug('Done %s', command)
            return True
        except Exception as e:
            self._logger.error('Error handling command %s: %s', command, str(e))
            return False
