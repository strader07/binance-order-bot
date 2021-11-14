import logging

from bot.commands import CommandParser
from bot.commands.message import MessageParser
from bot.commands.queue import CommandQueue
from bot.data.store import KeyStore
from bot.ui.telegram import TelegramApi, UserCommandsHandler


class UserCommandsPoller(object):
    LAST_OFFSET_KEY = 'poll_offset'

    def __init__(self, queue: CommandQueue, command_parser: CommandParser, message_parser: MessageParser,
                 api: TelegramApi, key_store: KeyStore, logger: logging.Logger):
        self._handler = UserCommandsHandler(queue, command_parser, message_parser, logger)
        self._api = api
        self._key_store = key_store
        self._logger = logger

    def poll(self, poll_timeout: int = 0):
        last_offset = self._key_store.get(self.LAST_OFFSET_KEY)
        if last_offset is not None:
            last_offset = int(last_offset) + 1
            self._logger.info('Polling %d, last offset %d', poll_timeout, last_offset)
        else:
            self._logger.info('Polling %d, no last offset', poll_timeout)

        updates = self._api.get_updates(offset=last_offset, timeout=poll_timeout)
        for update in updates:
            try:
                self._process_update(update)
            finally:
                last_offset = update['update_id']
                self._logger.debug('last offset %d', last_offset)
                self._key_store.put(self.LAST_OFFSET_KEY, str(last_offset))

    def _process_update(self, update):
        self._handler.process_update(update)
