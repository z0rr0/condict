#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from aside import *
from condt import Condt
import getpass, os

CONF_NAME = 'condt.conf' 
PREFIX = "{0}@ConDict>>>"


def main():
    global CONF_NAME, PREFIX
    # user-name query
    config = get_config_data(CONF_NAME)
    if not os.path.exists(config['database']):
        print("Not fount SQLite database")
        return 1
    # get name
    user = config['defuser'] if config['defuser'] else input("User name:")
    # create object
    account = Condt(user, config['database'])
    if not account:
        print('Validation error, bye...')
        return 0
    print(account)
    prefix = PREFIX.format(account.name)
    while (True):
        command = input(prefix)
        print('ok', command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Press Ctrl+C, Bye')
