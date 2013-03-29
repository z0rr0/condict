#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import re, configparser, json, signal
from urllib import request, parse

YANDEX_TRANSLATE_JSON = "http://translate.yandex.net/api/v1/tr.json/translate?"
YANDEX_SPELL_JSON = "http://speller.yandex.net/services/spellservice.json/checkText?"
TEST_CONNECT = "http://ya.ru/"
CHECK_MANY_SPACE = re.compile(r"\s+")
DEFCTEST = 10

def get_config_data(filename):
    global DEFCTEST
    result = {'database': None, 'defuser': None, 'defctest': DEFCTEST, 'debug': False}
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        for sec in config.sections():
            if 'dbname' in config[sec]:
                result['database'] = config[sec]['dbname']
            if 'default_user' in config[sec]:
                result['defuser'] = config[sec]['default_user']
            if 'test_count' in config[sec]:
                result['defctest'] = int(config[sec]['test_count'])
            if 'debug' in config[sec]:
                result['debug'] = config[sec].getboolean('debug')
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
    params = {'lang': trans_types[trans_type], 'text': for_translate}
    prepate_url = parse.urlencode(params, encoding="utf-8")
    try:
        conn = request.urlopen(YANDEX_TRANSLATE_JSON + prepate_url)
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

def check_spell(for_spelling, spell_type='en'):
    global YANDEX_SPELL_JSON
    result = False
    # options = IGNORE_DIGITS(2) + IGNORE_DIGITS(4) + IGNORE_CAPITALIZATION(512) + [BY_WORDS(256)]
    params = {'lang': spell_type, 'text': for_spelling, 'format': 'plane', 'options': 518}
    prepate_url = parse.urlencode(params, encoding="utf-8")
    erro_codes = ("ERROR_UNKNOWN_WORD",
        "ERROR_REPEAT_WORD",
        "ERROR_CAPITALIZATION",
        "ERROR_TOO_MANY_ERRORS")
    try:
        conn = request.urlopen(YANDEX_SPELL_JSON + prepate_url, None, 1)
        if conn.status == 200:
            from_url = conn.read().decode('utf-8')
            result = json.loads(from_url)
    except Exception as e:
        print("Not connection\nError: ".format(e))
        return result
    else:
        conn.close()
    if len(result) > 0:
        print("Spelling: ", end="")
        for_result = []
        for res in result:
            for_result.append("{0} -> {1}".format(res['word'], res['s']))
        print("; ".join(for_result))
    return 0

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