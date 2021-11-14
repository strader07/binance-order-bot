import argparse
import json
import os
import sys

import settings

from bot.ui.telegram import TelegramApi


def add_hook(args):
    if not args.bot_token:
        raise RuntimeError('required --bot-token or --bot-token-file')
    if not args.hook_url:
        raise RuntimeError('required --hook-url')

    api = TelegramApi(bot_token=args.bot_token)
    api.set_webhook(url=args.hook_url)


def remove_hook(args):
    if not args.bot_token:
        raise RuntimeError('required --bot-token')

    api = TelegramApi(bot_token=args.bot_token)
    api.delete_webhook()


ACTIONS = {
    'addhook': add_hook,
    'removehook': remove_hook
}


def load_config(args):
    if not os.path.exists(settings.CONFIG_FILE):
        return

    with open(settings.CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    if not args.bot_token and not args.bot_token_file:
        args.bot_token = config_data['bot_token']


def handle_special_args(args):
    if args.bot_token_file and not args.bot_token:
        with open(args.bot_token_file, 'r') as f:
            args.bot_token = f.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, help='action to perform',
                        choices=ACTIONS.keys())
    parser.add_argument('--bot-token', type=str, action='store', required=False, dest='bot_token',
                        help='Token for telegram bot. Used with actions: addhook, removehook')
    parser.add_argument('--bot-token-file', type=str, action='store', required=False, dest='bot_token_file',
                        help='File containing token for telegram bot. Used with actions: addhook, removehook')
    parser.add_argument('--hook-url', type=str, action='store', required=False, dest='hook_url',
                        help='Web-hook address for telegram bot. Used with actions: addhook')

    args = parser.parse_args(sys.argv[1:])
    load_config(args)
    handle_special_args(args)

    action = ACTIONS[args.action]
    action(args)


if __name__ == '__main__':
    main()
