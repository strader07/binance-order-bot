from typing import List


class Message(object):

    def __init__(self, text, source_name):
        self._text = text
        self._source_name = source_name

    @property
    def text(self) -> str:
        return self._text

    @property
    def source_name(self) -> str:
        return self._source_name

    def __eq__(self, other):
        return isinstance(other, Message) and \
               self.text == other.text and \
               self.source_name == other.source_name

    def __repr__(self):
        return '{}: {}'.format(self.source_name, self.text)


class MessageParser(object):

    def parse_all(self, data: List[dict]) -> List[Message]:
        return [self.parse(msg) for msg in data]

    def parse(self, data: dict) -> Message:
        message = data['message']
        if 'text' in message:
            text = message['text']
        else:
            text = message['caption']

        if 'forward_from_chat' in message:
            source_name = message['forward_from_chat']['title']
        else:
            source_name = message['chat']['first_name'] + ' ' + message['chat']['last_name']

        return Message(text, source_name)
