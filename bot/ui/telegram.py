import logging

import requests

from bot.commands import CommandParser
from bot.commands.message import MessageParser
from bot.commands.queue import CommandQueue


class TelegramApi(object):

    def __init__(self, bot_token: str, api_url: str = 'https://api.telegram.org/bot'):
        self._api_url = api_url + bot_token
        self._session = requests.session()

    def set_webhook(self, url: str):
        params = {
            'url': url,
            'allowed_updates': ['message']
        }

        return self._send_request('/setWebhook', params=params)

    def delete_webhook(self):
        return self._send_request('/deleteWebhook')

    def get_updates(self, offset: int = None, timeout: int = 0):
        params = {
            'allowed_updates': ['message'],
            'timeout': timeout
        }

        if offset:
            params['offset'] = offset

        return self._send_request('/getUpdates', params=params)

    def _send_request(self, url, method='get', params=None):
        if params is None:
            params = dict()

        request_url = self._api_url + url
        response = self._session.request(method, request_url, params=params)

        data = response.json()
        if not data['ok']:
            raise ValueError('request fail ' + str(data))
        return data['result']


class UserCommandsHandler(object):

    def __init__(self, queue: CommandQueue, command_parser: CommandParser,
                 message_parser: MessageParser, logger: logging.Logger):
        self._queue = queue
        self._command_parser = command_parser
        self._message_parser = message_parser
        self._logger = logger

    def process_update(self, update):
        self._logger.debug('Processing update %s', update)

        message = self._message_parser.parse(update)
        self._logger.info('New Message')

        if not self._command_parser.can_parse(message):
            self._logger.warning('Cannot parse message %s', message)
            return

        command = self._command_parser.parse(message)
        self._logger.info('New command %s', command)

        self._queue.store(command)
