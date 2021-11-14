from bot.commands.command import Command
from bot.commands.message import Message
from bot.commands.queue import CommandQueue
from bot.data.error import ErrorTracker
from bot.orders.binance_api import Binance
from bot.orders.tracking.tracker import OrderTracker
from bot.commands.parsers import CommandParser, CommandParserZhalgoul, CommandParserBPS
from bot.commands.handlers import CommandHandler, BuyCommandHandler, SellCommandHandler


class FullCommandParser(CommandParser):

    def __init__(self):
        self._all_parsers = [
            CommandParserZhalgoul(),
            CommandParserBPS()
        ]

    def can_parse(self, message: Message) -> bool:
        for parser in self._all_parsers:
            if parser.can_parse(message):
                return True
        return False

    def parse(self, message: Message) -> Command:
        for parser in self._all_parsers:
            if parser.can_parse(message):
                return parser.parse(message)

        raise ValueError('No parser that can handle message')


class FullCommandHandler(CommandHandler):

    def __init__(self, order_tracker: OrderTracker, binance: Binance, command_queue: CommandQueue,
                 error_tracker: ErrorTracker):
        self._all_handlers = [
            BuyCommandHandler(order_tracker, binance),
            SellCommandHandler(order_tracker, binance, command_queue, error_tracker)
        ]

    def can_handle(self, command: Command) -> bool:
        for handler in self._all_handlers:
            if handler.can_handle(command):
                return True
        return False

    def handle(self, command: Command):
        for handler in self._all_handlers:
            if handler.can_handle(command):
                return handler.handle(command)

        raise ValueError('No handler that can handle command')
