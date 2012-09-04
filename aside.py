#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import re, configparser, json
from urllib import request

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
    result = False
    prepate_url = request.pathname2url(for_translate)
    trans_types = {'en': 'en-ru', 'ru': 'ru-en'}
    prepate_url = "http://translate.yandex.net/api/v1/tr.json/translate?lang=" + trans_types[trans_type] + "&text=" + prepate_url
    try:
        conn = request.urlopen(prepate_url)
    except Exception:
        return result
    if conn.status == 200:
        try:
            from_url = conn.read().decode('utf-8')
            result = json.loads(from_url)
        except Exception as e:
            print(e)
    conn.close()
    return result

# Alternative
# import http.client
# def get_translate(for_translate, trans_type):
#     prepate_url = request.pathname2url(for_translate)
#     trans_types = {'en': 'en-ru', 'ru': 'ru-en'}
#     conn = http.client.HTTPConnection('translate.yandex.net')
#     result = False
#     try:
#         conn.request("GET", "/api/v1/tr.json/translate?lang=" + trans_types[trans_type] + "&text=" + prepate_url)
#         gr = conn.getresponse()
#     except Exception as e:
#         print(e)
#         conn.close()
#         return result
#     if gr.status == 200:
#         print(conn)
#         from_url = gr.read().decode('utf-8')
#         try:
#             result = json.loads(from_url)
#         except ValueError as e:
#             print(e)
#     conn.close()
#     return result
