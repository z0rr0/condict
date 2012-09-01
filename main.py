#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from aside import *
from condt import Condt
import getpass, os

CONF_NAME = 'condt.conf' 


def main():
    global CONF_NAME
    # user-name query
    config = get_config_data(CONF_NAME)
    print(config['database'])
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




if __name__ == "__main__":
    main()