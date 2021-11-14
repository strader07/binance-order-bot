import logging

from mockito import mock, when, verify, spy2

from bot.commands import Command
from bot.commands.queue import CommandQueueProcessor, CommandQueue, CommandHandler
from bot.util.iterator import EmptyIterator


class TestCommandQueueProcessor(object):

    def test_process_all_iterates_on_all_commands(self):
        commands = [
            mock(spec=Command),
            mock(spec=Command),
            mock(spec=Command)
        ]
        copy_commands = list(commands)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_commands.pop() if len(copy_commands) > 0 else None)

        queue = mock(spec=CommandQueue)
        when(queue).iterator().thenReturn(iterator)

        handler = mock(spec=CommandHandler)
        processor = CommandQueueProcessor(queue, handler, mock(spec=logging.Logger))
        spy2(processor.process)
        when(processor).process(...).thenReturn(True)

        processor.process_all()

        verify(processor, times=len(commands)).process(...)

    def test_process_all_handled_commands_are_deleted(self):
        commands = [
            mock(spec=Command),
            mock(spec=Command),
            mock(spec=Command)
        ]
        copy_commands = list(commands)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_commands.pop() if len(copy_commands) > 0 else None)

        queue = mock(spec=CommandQueue)
        when(queue).iterator().thenReturn(iterator)

        handler = mock(spec=CommandHandler)
        processor = CommandQueueProcessor(queue, handler, mock(spec=logging.Logger))
        spy2(processor.process)
        when(processor).process(...).thenReturn(True)

        processor.process_all()

        verify(iterator, times=len(commands)).delete()

    def test_process_all_not_handled_commands_not_deleted(self):
        commands = [
            mock(spec=Command),
            mock(spec=Command),
            mock(spec=Command)
        ]
        copy_commands = list(commands)
        iterator = mock(spec=EmptyIterator)
        when(iterator).__enter__().thenReturn(iterator)
        when(iterator).__exit__().thenReturn(None)
        when(iterator).next().thenAnswer(lambda: copy_commands.pop() if len(copy_commands) > 0 else None)

        queue = mock(spec=CommandQueue)
        when(queue).iterator().thenReturn(iterator)

        handler = mock(spec=CommandHandler)
        processor = CommandQueueProcessor(queue, handler, mock(spec=logging.Logger))
        spy2(processor.process)
        when(processor).process(...).thenReturn(False)

        processor.process_all()

        verify(iterator, times=0).delete()

    def test_process_command_cant_handle_returns_false(self):
        queue = mock(spec=CommandQueue)

        handler = mock(spec=CommandHandler)
        when(handler).can_handle(...).thenReturn(False)

        command = mock(spec=Command)

        processor = CommandQueueProcessor(queue, handler, mock(spec=logging.Logger))
        result = processor.process(command)
        assert not result

    def test_process_command_can_handle_handles_returns_true(self):
        queue = mock(spec=CommandQueue)

        handler = mock(spec=CommandHandler)
        when(handler).can_handle(...).thenReturn(True)

        command = mock(spec=Command)

        processor = CommandQueueProcessor(queue, handler, mock(spec=logging.Logger))
        result = processor.process(command)
        assert result

        verify(handler, times=1).handle(command)
