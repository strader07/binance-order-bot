import json
import threading
import time
import shutil
import os

import settings
from bot.bot import BotCommandProcessor, BotCommandPoller
from bot import dependencies


def main():
    for path in settings.RECREATE_DIRS:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)

    logger = dependencies.create_logger('main')

    with open(settings.CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    command_id_lock = threading.Lock()

    bot_processor = BotCommandProcessor(config_data, settings.PROCESSING_INTERVAL, command_id_lock)
    bot_poller = BotCommandPoller(config_data, settings.POLLING_INTERVAL, command_id_lock)

    processing_thread = threading.Thread(target=bot_processor.run_forever)
    polling_thread = threading.Thread(target=bot_poller.run_forever)

    logger.info('starting program')

    processing_thread.start()
    polling_thread.start()
    try:
        # Sleep forever, until something wakes us up,
        # like a KeyboardInterrupt
        while True:
            time.sleep(1)
    finally:
        bot_processor.stop()
        bot_poller.stop()

        logger.debug(u'waiting for threads to finish')
        processing_thread.join()
        polling_thread.join()

        logger.debug('done')


if __name__ == '__main__':
    main()
