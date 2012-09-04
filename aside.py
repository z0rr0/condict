#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import re, configparser

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

def get_command(raw_str):
	result = re.sub(r"\s+", " ", raw_str.strip())
	# return [command, str_params]
	return result.split(" ", 1)
