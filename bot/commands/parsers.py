from abc import ABC, abstractmethod
from bot.commands.command import Command, OrderTarget, OrderType
from bot.commands.message import Message

import re


class CommandParser(ABC):
    @abstractmethod
    def can_parse(self, message: Message) -> bool:
        pass

    @abstractmethod
    def parse(self, message: Message) -> Command:
        pass


class GenericCommandParser(CommandParser):

    def __init__(self, identifier_regex, symbol_regex, targets_data):
        self._identifier_regex = identifier_regex
        self._symbol_regex = symbol_regex
        self._targets_data = targets_data

    def can_parse(self, message: Message) -> bool:
        match = self._identifier_regex.match(message.text)
        return match is not None

    def parse(self, message: Message) -> Command:
        symbol = self._symbol_regex.match(message.text).group(1)
        targets = [OrderTarget(int(regex.match(message.text).group(1)), percentage)
                   for regex, percentage in self._targets_data]

        return Command(symbol, targets, OrderType.BUY, message.source_name)


class CommandParserZhalgoul(GenericCommandParser):
    _IDENTIFIER_REGEX = re.compile(r'^\s{0,20}BUY.*', re.DOTALL | re.MULTILINE)
    _SYMBOL_REGEX = re.compile(r'.*BUY\s?:\s+([A-Z]+)', re.DOTALL | re.MULTILINE)
    _TARGETS_REGEX = [
        (re.compile(r'.*Target.*1\s+:\s+(\d+)', re.DOTALL | re.MULTILINE), 1)
    ]

    def __init__(self):
        super().__init__(self._IDENTIFIER_REGEX, self._SYMBOL_REGEX, self._TARGETS_REGEX)


class CommandParserBPS(GenericCommandParser):
    _IDENTIFIER_REGEX = re.compile(r'^\s{0,20}#.*', re.DOTALL | re.MULTILINE)
    _SYMBOL_REGEX = re.compile(r'\s{0,20}#([A-Z]+)\s+', re.DOTALL | re.MULTILINE)
    _TARGETS_REGEX = [
        (re.compile(r'.*1⃣\s?(\d+)\s', re.DOTALL | re.MULTILINE), 0.35),
        (re.compile(r'.*2⃣\s?(\d+)\s', re.DOTALL | re.MULTILINE), 0.5),
        (re.compile(r'.*3⃣\s?(\d+)\s', re.DOTALL | re.MULTILINE), 0.15),
    ]

    def __init__(self):
        super().__init__(self._IDENTIFIER_REGEX, self._SYMBOL_REGEX, self._TARGETS_REGEX)
