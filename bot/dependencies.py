import json
import logging
import logging.handlers
import sys

from binance.client import Client

from bot.commands.factory import CommandFactory
from bot.commands.queue import CommandQueue
from bot.data.adapters import OrderToSheetRowAdpater, CommandToSheetRowAdapter
from bot.data.db import SqlExecutor, SqliteStore, SqliteKeyStore
from bot.data.error import ErrorTracker, RawAdapter
from bot.data.history import HistoryRecorder
from bot.data.sheets import Spreadsheet, SheetsStore
from bot.data.store import KeyStore
from bot.orders.binance_api import Binance
from bot.orders.tracking.reporter import OrderCompletionReporter
from bot.orders.tracking.tracker import OrderTracker
from bot.ui.telegram import TelegramApi


ORDER_TRACKER_NAME = 'tracked_orders'
QUEUED_COMMANDS_NAME = 'queued_commands'
COMPLETED_SELLS_NAME = 'completed'
FAILED_SELLS_NAME = 'failed_sells'
COMMANDS_HISTORY_NAME = 'commands'
ORDERS_HISTORY_NAME = 'orders'
ORDERS_COMPLETED_HISTORY_NAME = 'order_completed'
ORDERS_CANCELLED_HISTORY_NAME = 'order_cancelled'

COMMANDS_HISTORY_TABLE_DEF = '(symbol TEXT, targets TEXT, source_name TEXT, ordertype INTEGER, id INTEGER)'
ORDERS_HISTORY_TABLE_DEF = '(orderid INTEGER, targets TEXT, source_name TEXT, symbol TEXT, ordertype INTEGER)'
ORDERS_COMPLETED_HISTORY_TABLE_DEF = '(orderid INTEGER, targets TEXT, source_name TEXT, symbol TEXT, ordertype INTEGER)'
ORDERS_CANCELLED_HISTORY_TABLE_DEF = '(orderid INTEGER, targets TEXT, source_name TEXT, symbol TEXT, ordertype INTEGER)'

ORDER_TRACKER_TABLE_DEF = '(orderid INTEGER, targets TEXT, source_name TEXT, symbol TEXT, ordertype INTEGER)'
COMMANDS_QUEUE_TABLE_DEF = '(symbol TEXT, targets TEXT, source_name TEXT, ordertype INTEGER, id INTEGER)'
FAILED_SELLS_TABLE_DEF = '(symbol TEXT, targets TEXT, source_name TEXT, ordertype INTEGER, errors TEXT)'


def create_logger(name: str, file_path: str = None, max_bytes: int = 0,
                  backup_count: int = 0):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s, %(levelname)s] %(name)s: %(message)s')

    handler = logging.StreamHandler(sys.stdout,)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    if file_path:
        file_handler = logging.handlers.RotatingFileHandler(file_path,
                                                            maxBytes=max_bytes,
                                                            backupCount=backup_count,
                                                            encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)

    return logger


def create_error_tracker(sql_executor: SqlExecutor, logger: logging.Logger) -> ErrorTracker:
    sql_executor.create_table(FAILED_SELLS_NAME, FAILED_SELLS_TABLE_DEF)

    adapter = RawAdapter()
    failed_sells_store = SqliteStore(sql_executor, FAILED_SELLS_NAME, adapter)

    return ErrorTracker(failed_sells_store)


def create_history_recorder(sql_executor: SqlExecutor) -> HistoryRecorder:
    sql_executor.create_table(COMMANDS_HISTORY_NAME, COMMANDS_HISTORY_TABLE_DEF)
    sql_executor.create_table(ORDERS_HISTORY_NAME, ORDERS_HISTORY_TABLE_DEF)
    sql_executor.create_table(ORDERS_COMPLETED_HISTORY_NAME, ORDERS_COMPLETED_HISTORY_TABLE_DEF)
    sql_executor.create_table(ORDERS_CANCELLED_HISTORY_NAME, ORDERS_CANCELLED_HISTORY_TABLE_DEF)

    commands_store = SqliteStore(sql_executor, COMMANDS_HISTORY_NAME, CommandToSheetRowAdapter())
    orders_store = SqliteStore(sql_executor, ORDERS_HISTORY_NAME, OrderToSheetRowAdpater())
    order_completed = SqliteStore(sql_executor, ORDERS_COMPLETED_HISTORY_NAME, OrderToSheetRowAdpater())
    order_cancelled = SqliteStore(sql_executor, ORDERS_CANCELLED_HISTORY_NAME, OrderToSheetRowAdpater())

    return HistoryRecorder(commands_store, orders_store, order_completed, order_cancelled)


def create_spreadsheet(config_data: dict) -> Spreadsheet:
    return Spreadsheet(config_data['spreadsheet_id'], config_data['sheets_secrets_path'])


def create_binance(config_data: dict, logger: logging.Logger, test_order) -> Binance:
    with open(config_data['binance_secrets_path'], 'r') as f:
        secrets = json.load(f)
    client = Client(secrets['key'], secrets['secret'])
    return Binance(client, logger, test_order=test_order)


def create_telegram_api(config_data: dict):
    return TelegramApi(config_data['bot_token'])


def create_key_store(sql_executor: SqlExecutor, name: str) -> KeyStore:
    sql_executor.create_table(name, SqliteKeyStore.TABLE_COLUMNS_DEFINITION)
    return SqliteKeyStore(sql_executor, name)


def create_order_tracker(sql_executor: SqlExecutor, history_recorder: HistoryRecorder) -> OrderTracker:
    sql_executor.create_table(ORDER_TRACKER_NAME, ORDER_TRACKER_TABLE_DEF)

    adapter = OrderToSheetRowAdpater()
    store = SqliteStore(sql_executor, ORDER_TRACKER_NAME, adapter)

    return OrderTracker(store, history_recorder)


def create_commands_queue(sql_executor: SqlExecutor, history_recorder: HistoryRecorder,
                          factory: CommandFactory) -> CommandQueue:
    sql_executor.create_table(QUEUED_COMMANDS_NAME, COMMANDS_QUEUE_TABLE_DEF)

    adapter = CommandToSheetRowAdapter()
    store = SqliteStore(sql_executor, QUEUED_COMMANDS_NAME, adapter)

    return CommandQueue(store, history_recorder, factory)


def create_completion_reporter(spreadsheet: Spreadsheet, history_recorder: HistoryRecorder) -> OrderCompletionReporter:
    book = spreadsheet.open()
    adapter = OrderToSheetRowAdpater()
    store = SheetsStore(book, COMPLETED_SELLS_NAME, adapter)

    return OrderCompletionReporter(store, history_recorder)
