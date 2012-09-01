#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from aside import *
from condt import Condt
import getpass, os

CONF_NAME = 'condt.conf' 
DEBUG = True

def main():
    global CONF_NAME
    # user-name query
    config = get_config_data(CONF_NAME)
    print(config['database'])
    if not os.path.exists(config['database']):
        print("Not fount SQLite database")
        return 1
    # get name
    if config['defuser']:
        user = config['defuser']
    else:
        user = input("User name:")
    # get password
    print('"{0}" please enter your password:'.format(user))
    password = input("Password: ") if DEBUG else getpass.getpass()

    # create object
    account = Condt(user, password, config['database'])
    print(account)




if __name__ == "__main__":
    main()