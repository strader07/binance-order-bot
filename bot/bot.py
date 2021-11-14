import logging
import threading
import time

import settings
from bot import dependencies
from bot.commands import FullCommandParser, FullCommandHandler
from bot.commands.factory import CommandFactory
from bot.commands.message import MessageParser
from bot.commands.queue import CommandQueueProcessor
from bot.data.db import SqlExecutor
from bot.orders.tracking.tracker_checker import OrderStatusHandler, OrderTrackingTask
from bot.ui.poller import UserCommandsPoller


class BotCommandProcessor(object):

    def __init__(self, config_data: dict, interval: float, command_id_lock: threading.Lock):
        self._config_data = config_data
        self._interval = interval
        self._command_id_lock = command_id_lock
        self._run = True

    def run_forever(self):
        logger = dependencies.create_logger('processor',
                                            file_path=settings.LOG_FILE_FORMAT.format(name='processor'),
                                            max_bytes=settings.LOG_FILE_MAX_BYTES,
                                            backup_count=settings.LOG_FILE_BACKUP_COUNT)

        with SqlExecutor(settings.DATABASE_PATH) as sql_executor:
            error_tracker = dependencies.create_error_tracker(sql_executor, logger)
            history_recorder = dependencies.create_history_recorder(sql_executor)

            binance = dependencies.create_binance(self._config_data, logger, settings.BINANCE_TEST_ORDER)
            spreadsheet = dependencies.create_spreadsheet(self._config_data)

            key_store = dependencies.create_key_store(sql_executor, settings.KEY_STORE_TABLE_NAME)
            command_factory = CommandFactory(key_store, self._command_id_lock)

            order_tracker = dependencies.create_order_tracker(sql_executor, history_recorder)
            queue = dependencies.create_commands_queue(sql_executor, history_recorder, command_factory)
            command_handler = FullCommandHandler(order_tracker, binance, queue, error_tracker)

            completion_reporter = dependencies.create_completion_reporter(spreadsheet, history_recorder)
            status_handler = OrderStatusHandler(queue, completion_reporter, order_tracker, history_recorder)

            queue_processor = CommandQueueProcessor(queue, command_handler, logger)
            tracker = OrderTrackingTask(order_tracker, binance, status_handler, logger)

            self._do_run(queue_processor, tracker, logger)

    def stop(self):
        self._run = False

    def _do_run(self, queue_processor: CommandQueueProcessor,
                tracker: OrderTrackingTask, logger: logging.Logger):
        logger.debug('processor starting')
        while self._run:
            try:
                queue_processor.process_all()
                tracker.do_check()
            except Exception as e:
                logger.error('Error in bot processor %s', str(e))
            finally:
                time.sleep(self._interval)
        logger.debug('processor done')


class BotCommandPoller(object):

    def __init__(self, config_data: dict, interval: float, command_id_lock: threading.Lock):
        self._config_data = config_data
        self._interval = interval
        self._command_id_lock = command_id_lock
        self._run = True

    def run_forever(self):
        logger = dependencies.create_logger('poller',
                                            file_path=settings.LOG_FILE_FORMAT.format(name='poller'),
                                            max_bytes=settings.LOG_FILE_MAX_BYTES,
                                            backup_count=settings.LOG_FILE_BACKUP_COUNT)

        with SqlExecutor(settings.DATABASE_PATH) as sql_executor:
            history_recorder = dependencies.create_history_recorder(sql_executor)

            key_store = dependencies.create_key_store(sql_executor, settings.KEY_STORE_TABLE_NAME)
            command_factory = CommandFactory(key_store, self._command_id_lock)

            queue = dependencies.create_commands_queue(sql_executor, history_recorder, command_factory)
            command_parser = FullCommandParser()
            message_parser = MessageParser()
            telegram_api = dependencies.create_telegram_api(self._config_data)

            command_poller = UserCommandsPoller(queue, command_parser, message_parser,
                                                telegram_api, key_store, logger)

            self._do_run(command_poller, logger)

    def stop(self):
        self._run = False

    def _do_run(self, command_poller: UserCommandsPoller, logger: logging.Logger):
        logger.debug('poller starting')
        while self._run:
            try:
                command_poller.poll(poll_timeout=settings.POLL_TIMEOUT)
            except Exception as e:
                logger.error('Error in bot poller %s', str(e))
            finally:
                time.sleep(self._interval)

        logger.debug('poller finished')
