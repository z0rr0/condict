#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import configparser

def get_config_data(filename):
    result = {'database': None, 'defuser': None}
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        result['database'] = config['database']['dbname']
        result['defuser'] = config['user']['default_user']
    except (KeyError, IndexError, TypeError) as er:
        pass
    return result

def help_command(commands):
    for key, item in commands.items():
        print("{0:.<30}{1}".format(key, item[0]))