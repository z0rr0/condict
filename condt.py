#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib, getpass
from aside import *

# please, change this stirg for your application
SALT = 'r8Uts$jLs74Lgh49_h75&w@dFsS4sgpm3Kqq['
DEBUG = True

class IncorrectDbData(Exception): pass

class BaseConDict(object):
    """Base Console Dictionary class"""
    def __init__(self, name, dbfile):
        self.connect = sqlite3.connect(dbfile)
        self.online = False
        self.name = name
    def __repr__(self):
        return "<ConDict object for {0}>".format(self.name)
    def __str__(self):
        return "<ConDict object for {0}>".format(self.name)
    def __bool__(self):
        valid = True if self.user_id else False
        return valid
    def __del__(self):
        self.connect.close()

class Condt(BaseConDict):
    """Condt - class for ConDict"""
    COMMANDS = {'.help': {'desc': 'list commands', 'command': None}, 
        '.chname': {'desc': 'change current user name', 'command': None},
        '.chpassword': {'desc': 'change current password', 'command': None},
        '.list': {'desc': 'list users words', 'command': None},
        '.en': {'desc': 'dictionary mode English to Russian', 'command': None},
        '.ru': {'desc': 'dictionary mode Russian to English', 'command': None},
        '.add': {'desc': 'add new words', 'command': None},
        '.connect': {'desc': 'test connection', 'command': None},
        # '.edit': {'desc': 'edit words', 'command': None},
        # '.del': {'desc': 'delete words', 'command': None},
        '.exit': {'desc': 'quit from program', 'command': None},
        }
    def __init__(self, name, dbfile):
        super().__init__(name, dbfile)       
        self.__pcounter = 3
        self.init_command()
        self.user_id = self.get_user()
        self.command_connect()

    def get_user(self):
        sqlstr="SELECT id FROM user WHERE name=(?) AND password=(?)"
        cur = self.connect.cursor()
        ch_user_id = self.check_name(cur)
        if ch_user_id:
            ch_user_id = ch_user_id[0]
            # check pass
            user_id = self.handling_action(cur, ch_user_id)
        else:
            user_id = self.handling_add(cur)
        cur.close()
        return user_id

    def init_command(self):
        self.COMMANDS['.help']['command'] = self.command_help
        self.COMMANDS['.exit']['command'] = self.command_exit
        self.COMMANDS['.chname']['command'] = self.command_chname
        self.COMMANDS['.chpassword']['command'] = self.command_chpassword
        self.COMMANDS['.list']['command'] = self.command_list
        self.COMMANDS['.en']['command'] = self.command_en
        self.COMMANDS['.ru']['command'] = self.command_ru
        self.COMMANDS['.add']['command'] = self.command_add
        self.COMMANDS['.connect']['command'] = self.command_connect

    def hash_pass(self, password):
        result = bytes(password.strip() + SALT, 'utf-8')
        result = bytes(hashlib.md5(result).hexdigest(), 'utf-8')
        return hashlib.sha1(result).hexdigest()

    def check_name(self, cur):
        try:
            cur.execute("SELECT id FROM user WHERE name=(?)", (self.name,))
        except sqlite3.DatabaseError as er:
            return None
        return cur.fetchone()

    def check_password(self, cur, user_id, password):
        try:
            cur.execute("SELECT id FROM user WHERE id=(?) AND password=(?)", (user_id, self.hash_pass(password)))
        except sqlite3.DatabaseError as er:
            return None
        return cur.fetchone()

    def handling_action(self, cur, ch_user_id):
        print('"{0}" please enter your password:'.format(self.name))
        self.password = input("Password:") if DEBUG else getpass.getpass()
        while(self.__pcounter > 0):
            user_id = self.check_password(cur, ch_user_id, self.password)
            if user_id:
                return user_id[0]
            else:
                action = input('Invalid password, there are actions "Exit"/"Press password again" [e/P]:')
                if action in ('', 'P', 'p'):
                    self.__pcounter -= 1
                    self.password = input("Password:") if DEBUG else getpass.getpass()
                elif action in ('e', 'E'):
                    break
                else:
                    print('select an option...')
        return None

    def handling_add(self, cur):
        while(True):
            want_add = input('Are you want add new user? [Y/n]')
            if want_add in ('', 'y', 'Y'):
                name = input("You login [{0}]:".format(self.name))
                if name == '':
                    name = self.name
                fullname = input("You full name (optional):")
                password = input("Password:") if DEBUG else getpass.getpass()
                transaction_ok = False
                try:
                    cur.execute("INSERT INTO user (name, password, full) VALUES (?,?,?)", (name, self.hash_pass(password), fullname))
                except sqlite3.DatabaseError as er:
                    print('Incorrect information, change data')
                    continue
                else:
                    self.connect.commit()
                if cur.rowcount == -1:
                    print('Incorrect information, change data')
                    continue
                self.name = name
                self.password = self.hash_pass(password)
                return cur.lastrowid
            elif want_add in ('n', 'N'):
                break
            else:
                print('select an option...')
        return None

    def handling_command(self, command):
        command, arg = get_command(command)
        if command not in self.COMMANDS.keys():
            return None
        result = self.COMMANDS[command]['command'](arg)
        return result

    def command_help(self, arg=None):
        for key, item in self.COMMANDS.items():
            print("{0:.<30}{1}".format(key, item['desc']))
        return '.help'

    def command_exit(self, arg=None):
        return 0

    def command_chname(self, arg=None):
        cur = self.connect.cursor()
        while(True):
            name = input("You login:")
            fullname = input("You full name (optional):")
            try:
                if name == '':
                    raise IncorrectDbData()
                cur.execute("UPDATE user SET name=(?), full=(?) WHERE id=(?)", (name, fullname, self.user_id))
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                print('Incorrect information, change data')
                e = input('Do you wand exit from name update [N/y]?')
                if e in ('y', 'Y'):
                    break
                continue
            else:
                self.connect.commit()
                self.name = name
                print("You name updated successfully")
                break
        cur.close()
        return 'chname'

    def command_chpassword(self, arg=None):
        cur = self.connect.cursor()
        while(True):
            password_old = input("Old password:") if DEBUG else getpass.getpass()
            try:
                if self.check_password(cur, self.user_id, password_old):
                    password1 = input("New password:") if DEBUG else getpass.getpass()
                    password2 = input("New password again:") if DEBUG else getpass.getpass()
                    if password1 != password2:
                        raise IncorrectDbData()
                    else:
                        cur.execute("UPDATE user SET password=(?) WHERE id=(?)", (self.hash_pass(password1), self.user_id))
                else:
                    raise IncorrectDbData()
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                print('Incorrect information, change data')
                e = input('Do you wand exit from password update [N/y]?')
                if e in ('y', 'Y'):
                    break
                continue
            else:
                self.connect.commit()
                self.password = password1
                print("You password updated successfully")
                break
        cur.close()
        return 'chpassword'

    def command_en(self, text):
        print(self.command_enru(text, 'en'))
        return 'en'
    def command_ru(self, text):
        print(self.command_enru(text, 'ru'))
        return 'ru'
    def command_enru(self, text, tr_type):
        if not self.online:
            return "Offline, please test connect with '.connect' command"
        result = get_translate(text, tr_type)
        if not result or result['code'] != 200:
            self.command_connect()
            return "Error, not foud translate"
        return result['text']

    def command_list(self, pattern=None):
        cur = self.connect.cursor()
        sql_list = "SELECT `translate`.`id`, `term`.`en`, `translate`.`rus`, `progress`.`all`, `progress`.`error` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) LEFT JOIN `progress` ON (`progress`.`translate_id`=`translate`.`id`) WHERE `translate`.`user_id`=(?) "
        params = (self.user_id,)
        result_text, result_param = "Get {0} rows", [0]
        if pattern:
            sql_list += " AND `term`.`en` LIKE (?)"
            params = (self.user_id, pattern + '%')
            result_text = "Get {0} rows for pattern '{1}%'"
            result_param.append(pattern)
        sql_list += " ORDER BY `translate`.`created` DESC"
        try:
            cur.execute(sql_list, params)
            i = 1
            for row in cur.fetchall():
                print("{0}. ID={1} all {2}, error {3}".format(i, row[0], row[3], row[4]))
                print("\t(en) {0}\n\t(ru) {1}".format(row[1], row[2]))
                i +=1
            result_param[0] = i - 1
            print(result_text.format(*result_param))
        except (sqlite3.DatabaseError, IncorrectDbData) as er:
            print('Sorry, error')
            return 'list'
        cur.close()
        return 'list'
    
    def command_add(self, en_words=None):
        cur = self.connect.cursor()
        print('Please enter your patterns:')
        while True:
            try:
                en = input('En [' + en_words + ']:') if en_words else input('En: ')
                if not en:
                    if not en_words:
                        raise IncorrectDbData()
                    else:
                        en = en_words
                try:
                    ru_words = self.command_enru(en, 'en')[0]
                except Exception as e:
                    if DEBUG: print(e)
                    ru_words = None
                ru = input('Ru [' + ru_words + ']:') if ru_words else input('Ru: ')
                if not ru:
                    if not ru_words:
                        raise IncorrectDbData()
                    else:
                        ru = ru_words
                ru = ru.lower().strip()
                en = en.lower().strip()
                token = hashlib.md5(bytes(en, 'utf-8')).hexdigest()
                # search token
                sql_list = "SELECT `token` FROM `term` WHERE `token`=(?)"
                cur.execute(sql_list, (token,))
                if cur.fetchone():
                    print('Words add already.')
                    break
                sql_list1 = "INSERT INTO `term` (`token`, `en`) VALUES ((?), (?))"
                cur.execute(sql_list1, (token, en))
                sql_list2 = "INSERT INTO `translate` (`term`, `user_id`, `rus`) VALUES (?, ?, ?)"
                cur.execute(sql_list2, (token, self.user_id, ru))
                sql_list3 = "INSERT INTO `progress` (`translate_id`) VALUES (?)"
                cur.execute(sql_list3, (cur.lastrowid,))
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                if DEBUG: print(er)
                print('Incorrect information, change data')
                ent = input('Do you wand enter new words [Y/n]?')
                if ent in ('n', 'N'):
                    break
                continue
            else:
                self.connect.commit()
                break
        cur.close()
        return 'add'

    def command_edit(self, translate_id):
        pass
    def command_delete(self, id_or_pattern):
        pass

    def command_connect(self, arg=None):
        result = get_test_connection()
        if result:
            print("Ok connection")
        else:
            print("Error connection")
        self.online = result
        return 'connect'
