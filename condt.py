#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib, getpass, datetime, csv
from aside import *

# please, change this stirg for your application
SALT = 'r8Uts$jLs74Lgh49_h75&w@dFsS4sgpm3Kqq['
EXPORT_NAME = 'condict_export_'
DEBUG = True

class IncorrectDbData(Exception): pass
class DublicationDbData(Exception): pass

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
        '.export': {'desc': 'export user dictionary to CSV file', 'command': None},
        '.edit': {'desc': 'edit words', 'command': None},
        '.delete': {'desc': 'delete words', 'command': None},
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
        self.COMMANDS['.export']['command'] = self.command_export
        self.COMMANDS['.edit']['command'] = self.command_edit
        self.COMMANDS['.delete']['command'] = self.command_delete

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
        sql_list += " ORDER BY `translate`.`created` DESC, `term`.`token`"
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
        """add new user pattern"""
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
                translate_id = self.command_add_kinds(cur, en, ru)
            except DublicationDbData:
                print('Words already contained in database. For search use ".list {0}"'.format(en))
                break
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                if DEBUG: print(er)
                print('Incorrect information, change data')
                ent = input('Do you wand enter new words [Y/n]?')
                if ent in ('n', 'N'):
                    break
                continue
            else:
                self.connect.commit()
                print("Words added successfully, ID={0}".format(translate_id))
                break
        cur.close()
        return 'add'

    def command_add_kinds(self, cur, en, ru):
        """SQL queries for add-command"""
        token = hashlib.md5(bytes(en, 'utf-8')).hexdigest()
        # search token
        sql_list = "SELECT `token` FROM `term` WHERE `token`=(?)"
        cur.execute(sql_list, (token,))
        # if cur.fetchone(): raise DublicationDbData()
        if not cur.fetchone():
            # insert in to tables
            sql_list1 = "INSERT INTO `term` (`token`, `en`) VALUES ((?), (?))"
            cur.execute(sql_list1, (token, prepare_str(en)))
        cur.execute("SELECT `id` FROM `translate` WHERE `term`=(?) AND `user_id`=(?)", (token, self.user_id))
        if cur.fetchone(): raise DublicationDbData()
        sql_list2 = "INSERT INTO `translate` (`term`, `user_id`, `rus`) VALUES (?, ?, ?)"
        cur.execute(sql_list2, (token, self.user_id, prepare_str(ru)))
        translate_id = cur.lastrowid
        sql_list3 = "INSERT INTO `progress` (`translate_id`) VALUES (?)"
        cur.execute(sql_list3, (translate_id,))
        return translate_id

    def command_export(self, arg=None):
        """export all user dictionary in CSV file"""
        global EXPORT_NAME, DEBUG
        if arg:
            export_name = arg + ".csv"
        else:
            d = datetime.date.today()
            export_name = EXPORT_NAME + d.strftime("%Y_%m_%d") + ".csv"
        try:
            cur = self.connect.cursor()
            writer_csv = csv.writer(open(export_name, 'w'), delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer_csv.writerow(['ENGLISH','RUSSIAN'])
            sql_list = "SELECT `term`.`en`, `translate`.`rus` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) WHERE `translate`.`user_id`=(?) ORDER BY `term`.`en`, `translate`.`rus`"
            cur.execute(sql_list, (self.user_id,))
            for result in cur.fetchall():
                writer_csv.writerow(result)
        except Exception as e:
            if DEBUG: print(e)
            print("Export error")
        else:
            cur.close()
            print("Export finished successfully to file: {0}".format(export_name))
        return 'export'

    def command_edit(self, translate_id):
        """Edit translate words form DB, search by ID"""
        # search id
        cur = self.connect.cursor()
        try:
            translate_id = int(translate_id)
            result = self.check_user_translate(cur, translate_id)
            if not result: 
                raise IncorrectDbData()
            else:
                result = result[0]
            # enter en-ru
            en = input('En [' + result[0] + ']:')
            if not en: en = result[0]
            ru = input('Ru [' + result[1] + ']:')
            if not ru: ru = result[1]
            # new token
            need_del = False
            token = hashlib.md5(bytes(en, 'utf-8')).hexdigest()
            if token != result[2]:
                cur.execute("INSERT INTO `term` (`token`, `en`) VALUES ((?), (?))", (token, prepare_str(en)))
                need_del = True
            # translate
            cur.execute("UPDATE `translate` SET `rus`=(?), `term`=(?) WHERE `term`=(?) AND `user_id`=(?)", (prepare_str(ru), token, result[2], self.user_id))
            # delete recodrs in term if it needed
            if need_del:
                cur.execute("SELECT `id` FROM `translate` WHERE `term`=(?) LIMIT 1", (result[2],))
                if not cur.fetchone(): cur.execute("DELETE FROM `term` WHERE `token`=(?)", (result[2],))
        except IncorrectDbData as e:
            print('Record not found for current user.')
        except (TypeError, ValueError, sqlite3.DatabaseError) as er:
            if DEBUG: print(er)
            print("Error, use '.edit ID' (ID is numerical)")
        else:
            self.connect.commit()
            cur.close()
            print('Successfully update')
        return 'edit'

    def command_delete(self, id_or_pattern):
        """Delete translate words form DB, search by ID or pattern (several rows)"""
        cur = self.connect.cursor()
        try:
            try:
                pattern = int(id_or_pattern) 
                by_pattern = False
            except ValueError as e:
                pattern = id_or_pattern
                by_pattern = True
            result = self.check_user_translate(cur, pattern, by_pattern)
            if not result: raise IncorrectDbData()
            print('Records for delete:')
            id_for_del = []
            for row in result:
                # id, token
                id_for_del.append((row[3], row[2]))
                print("ID={0}:\t'{1}'".format(row[3], row[0]))
            correction = input("It is right [N/y]?")
            if correction not in ('Y', 'y'):
                return 'delete'
            # delete for correction information
            for rec in id_for_del:
                # delete translate
                cur.execute("DELETE FROM `translate` WHERE `id`=(?)", (rec[0],))
                # delete progress
                cur.execute("DELETE FROM `progress` WHERE `translate_id`=(?)", (rec[0],))
                # del from term if it needed
                cur.execute("SELECT `term` FROM `translate` WHERE `term`=(?) LIMIT 1", (rec[1],))
                if not cur.fetchone():
                    cur.execute("DELETE FROM `term` WHERE `token`=(?)", (rec[1],))
        except IncorrectDbData as e:
            print('Record not found for current user.')
        except (sqlite3.DatabaseError, TypeError) as er:
            if DEBUG: print(er)
            print("Error, use '.delete [ID or pattern]' (ID is numerical)")
        else:
            self.connect.commit()
            cur.close()
            print('Successfully update')
        return 'delete'

    def command_connect(self, arg=None):
        """test connection, set user status"""
        result = get_test_connection()
        if result:
            print("Ok connection")
        else:
            print("Error connection")
        self.online = result
        return 'connect'

    def check_user_translate(self, cur, for_search, by_pattern=False):
        sql_str = "SELECT `term`.`en`, `translate`.`rus`, `term`.`token`, `translate`.`id` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) "
        if by_pattern:
            pattern = for_search + '%' 
            sql_str += "WHERE `term`.`en` LIKE (?) AND `user_id`=(?) ORDER BY `translate`.`id`"
        else:
            pattern = for_search
            sql_str += "WHERE `translate`.`id`=(?) AND `user_id`=(?) ORDER BY `translate`.`id`"
        cur.execute(sql_str, (pattern, self.user_id))
        return cur.fetchall()
