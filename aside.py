#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import re, configparser, json, signal
from urllib import request

YANDEX_TRANSLATE_JSON = "http://translate.yandex.net/api/v1/tr.json/translate?lang="
TEST_CONNECT = "http://ya.ru/"

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
    command = result.split(" ", 1)
    if len(command) == 1:
        command.append([])
    return command

def get_translate(for_translate, trans_type):
    global YANDEX_TRANSLATE_JSON
    result = False
    prepate_url = request.pathname2url(for_translate)
    trans_types = {'en': 'en-ru', 'ru': 'ru-en'}
    prepate_url = YANDEX_TRANSLATE_JSON + trans_types[trans_type] + "&text=" + prepate_url
    try:
        conn = request.urlopen(prepate_url)
    except Exception as e:
        print("Not connection\nError:")
        print(e)
        return result
    if conn.status == 200:
        try:
            from_url = conn.read().decode('utf-8')
            result = json.loads(from_url)
        except Exception as e:
            print(e)
    conn.close()
    return result

def get_test_connection():
    global TEST_CONNECT
    try:
        conn = request.urlopen(TEST_CONNECT)
        result = True if conn.getcode() == 200 else False
    except Exception as e:
        print('Test connection False,', e)
        return False
    conn.close()
    return result 