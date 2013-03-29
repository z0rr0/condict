#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from aside import *
from condt import Condt
import getpass, os

CONF_NAME = 'condt.conf' 
PREFIX = "{0}@condict[{1}]$"
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
    account = Condt(user, config['database'], config['debug'], config['defctest'])
    if not account:
        print('Validation error, by...')
        return 0
    print(WELCOM)
    while (True):
        conn_status = 'online' if account.online else 'offline'
        prefix = PREFIX.format(account.name, conn_status)
        command = input(prefix)
        get_command = account.handling_command(command)
        if get_command is None:
            print('Sorry, unknown command: "{0}"\nuse ".help" for more information'.format(command))
            continue
        if not get_command:
            print("By {0}!".format(account.name))
            return 0

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Press Ctrl+C, Bye')
