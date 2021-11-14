import logging

from bottle import Bottle, request as bottle_request

from bot.commands import CommandParser
from bot.commands.message import MessageParser
from bot.commands.queue import CommandQueue
from bot.ui.telegram import UserCommandsHandler


class HookHandler(Bottle):

    def __init__(self, queue: CommandQueue, command_parser: CommandParser, message_parser: MessageParser,
                 logger: logging.Logger):
        super(HookHandler, self).__init__()

        self._handler = UserCommandsHandler(queue, command_parser, message_parser, logger)

        self.route('/', callback=self.post_handler, method="POST")

    def post_handler(self):
        data = bottle_request.json
        # TODO: PROBABLY NEED TO EXTRACT FROM SOME KEY
        self._handler.process_update(data)
