import threading

from bot.commands import Command
from bot.data.store import KeyStore


class CommandFactory(object):
    _LAST_ID = 'command_last_id'

    def __init__(self, key_store: KeyStore, lock: threading.Lock):
        self._key_store = key_store
        self._lock = lock

    def create_from(self, command: Command) -> Command:
        if command.id > 0:
            return command

        self._lock.acquire()
        try:
            last_id = self._key_store.get(self._LAST_ID)
            if last_id is None:
                last_id = 1
            else:
                last_id = int(last_id) + 1

            command._id = last_id
            self._key_store.put(self._LAST_ID, str(last_id))

            return command
        finally:
            self._lock.release()
