#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from aside import *
from condt import Condt
import getpass, os

CONF_NAME = 'condt.conf' 
PREFIX = "{0}@ConDict>>>"
WELCOM = """****************************************************
*** Good day.                                    ***
*** For help, use the command ".help", nice work.***
****************************************************"""

def main():
    global CONF_NAME, PREFIX
    # user-name query
    config = get_config_data(CONF_NAME)
    if not config['database'] or not os.path.exists(config['database']):
        print("Not fount SQLite database")
        return 1
    # get name
    user = config['defuser'] if config['defuser'] else input("User name:")
    # create object
    account = Condt(user, config['database'])
    if not account:
        print('Validation error, bye...')
        return 0
    print(WELCOM)
    while (True):
        prefix = PREFIX.format(account.name)
        command = input(prefix)
        get_command = account.handling_command(command)
        if get_command is None:
            print('Sorry, unknown command: "{0}"\nuse ".help" for more information'.format(command))
            continue
        if not get_command:
            print("Bye {0}!".format(account.name))
            return 0
        # COMMANDS[command][1](COMMANDS)
        # print('ok', command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Press Ctrl+C, Bye')
