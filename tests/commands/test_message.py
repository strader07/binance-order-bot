import pytest
import json

from bot.commands.message import MessageParser
from tests.data_examples.telegram_messages import FORWARDED_FROM_CHAT_DATA_FORMAT, FROM_USER_DATA_FORMAT


# noinspection PyMethodMayBeStatic
class TestMessageParser(object):

    @pytest.fixture(scope='class')
    def forwarded_from_chat_message(self):
        text = """
I, I can't get these memories out of my mind
And some kind of madness has started to evolve
I, I tried so hard to let you go
But some kind of madness is swallowing me whole, yeah
                """
        title = "some big chat name"

        data = json.loads(
            FORWARDED_FROM_CHAT_DATA_FORMAT.format(text=text.replace('\n', '\\n'), first_name="whatever",
                                                   last_name="whatever2", title=title))
        return data, text, title

    @pytest.fixture(scope='class')
    def from_user_message(self):
        text = """
Revere a million prayers
And draw me into your holiness
But there's nothing there
Light only shines from those who share
Unleash a million drones
Confine me then erase me babe
Do you have no soul?
It's like it died long ago
        """
        first_name = "a name"
        last_name = "lol name"

        data = json.loads(FROM_USER_DATA_FORMAT.format(text=text.replace('\n', '\\n'), first_name=first_name,
                                                       last_name=last_name))
        return data, text, first_name + " " + last_name

    def test_forwarded_message_parses_correctly(self, forwarded_from_chat_message):
        data, expected_text, expected_source = forwarded_from_chat_message

        parser = MessageParser()
        message = parser.parse(data)

        assert message.text == expected_text
        assert message.source_name == expected_source

    def test_user_message_parses_correctly(self, from_user_message):
        data, expected_text, expected_source = from_user_message

        parser = MessageParser()
        message = parser.parse(data)

        assert message.text == expected_text
        assert message.source_name == expected_source
