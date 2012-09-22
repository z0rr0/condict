#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import re, configparser, json, signal
from urllib import request

YANDEX_TRANSLATE_JSON = "http://translate.yandex.net/api/v1/tr.json/translate?lang="
TEST_CONNECT = "http://ya.ru/"
CHECK_MANY_SPACE = re.compile(r"\s+")
DEFCTEST = 10

def get_config_data(filename):
    global DEFCTEST
    result = {'database': None, 'defuser': None, 'defctest': DEFCTEST}
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        result['database'] = config['database']['dbname']
        result['defuser'] = config['user']['default_user']
        result['defctest'] = int(config['user']['test_count'])
    except (ValueError, KeyError, IndexError, TypeError) as er:
        pass
    return result

def prepare_str(input_str):
    global CHECK_MANY_SPACE
    result = CHECK_MANY_SPACE.sub(" ", input_str.strip())
    return result

def get_command(raw_str):
    result = prepare_str(raw_str)
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
    print("check connection...")
    try:
        conn = request.urlopen(TEST_CONNECT)
        result = True if conn.getcode() == 200 else False
    except Exception as e:
        print('Test connection False,', e)
        return False
    conn.close()
    return result

def check_ans(answer, enter):
    global CHECK_MANY_SPACE
    a1 = CHECK_MANY_SPACE.sub(" ", answer.lower().strip())
    a2 = CHECK_MANY_SPACE.sub(" ", enter.lower().strip())
    return (a1 == a2)