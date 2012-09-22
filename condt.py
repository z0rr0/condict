#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib, getpass, datetime, csv, random
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
    def prer(self, error):
        global DEBUG
        if DEBUG: print(error)

class Condt(BaseConDict):
    """Condt - class for ConDict"""
    COMMANDS = {'.help': {'desc': 'list commands', 'command': None, 
            'full': 'output list commands'}, 
        '.chname': {'desc': 'change current user name', 'command': None,
            'full': 'change current info: login and name'},
        '.chpassword': {'desc': 'change current password', 'command': None,
            'full': 'change password for current password'},
        '.list': {'desc': 'list users words', 'command': None,
            'full': 'list user words/patterns, ".list" or ".list pattern"'},
        '.en': {'desc': 'dictionary mode English to Russian', 'command': None,
            'full': 'yandex translate English to Russian'},
        '.ru': {'desc': 'dictionary mode Russian to English', 'command': None,
            'full': 'yandex translate Russian to English'},
        '.add': {'desc': 'add new words', 'command': None,
            'full': 'add new word/pattern'},
        '.connect': {'desc': 'test connection', 'command': None,
            'full': 'test internet connection'},
        '.export': {'desc': 'export user dictionary', 'command': None,
            'full': 'export user dictionary to CSV file, encoding UTF-8'},
        '.import': {'desc': 'import user dictionary', 'command': None,
            'full': 'import user dictionary from CSV file, encoding UTF-8'},
        '.edit': {'desc': 'edit words', 'command': None,
            'full': 'edit word/pattern, search by ID ".edit ID"'},
        '.delete': {'desc': 'delete words', 'command': None,
            'full': 'delete word/pattern, search by ID, ".delete ID"'},
        '.exit': {'desc': 'quit from program', 'command': None,
            'full': 'quit form program'},
        '.test': {'desc': 'start test (default en)', 'command': None,
            'full': 'start en-ru test'},
        '.testru': {'desc': 'start ru-test', 'command': None,
            'full': 'start ru-en test'},
        '.testmix': {'desc': 'start en-ru test', 'command': None,
            'full': 'start mix test'},
        }
    def __init__(self, name, dbfile, ctest=10):
        super().__init__(name, dbfile)       
        self.__pcounter = 3
        self.ctest = ctest
        self.init_command()
        self.user_id = self.get_user()
        self.command_connect()

    def get_user(self):
        """get user ID by name and password"""
        sqlstr="SELECT id FROM user WHERE name=(?) AND password=(?)"
        cur = self.connect.cursor()
        ch_user_id = self.check_name(cur)
        if ch_user_id:
            ch_user_id = ch_user_id
            user_id = self.handling_action(cur, ch_user_id)
        else:
            user_id = self.handling_add(cur)
        cur.close()
        return user_id

    def init_command(self):
        """commands list"""
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
        self.COMMANDS['.import']['command'] = self.command_import
        self.COMMANDS['.edit']['command'] = self.command_edit
        self.COMMANDS['.delete']['command'] = self.command_delete
        self.COMMANDS['.test']['command'] = self.command_testen
        self.COMMANDS['.testru']['command'] = self.command_testru
        self.COMMANDS['.testmix']['command'] = self.command_testmix

    def hash_pass(self, password):
        """create password hash: text => hast string"""
        result = bytes(password.strip() + SALT, 'utf-8')
        result = bytes(hashlib.md5(result).hexdigest(), 'utf-8')
        return hashlib.sha1(result).hexdigest()

    def check_name(self, cur):
        """get user id by name - unique field"""
        uid = None
        try:
            cur.execute("SELECT id FROM user WHERE name=(?)", (self.name,))
            uid = cur.fetchone()
            if uid: uid = uid[0]
        except (sqlite3.DatabaseError, IndexError) as er:
            self.prer(er)
            return None
        return uid

    def check_password(self, cur, user_id, password):
        """check password"""
        try:
            cur.execute("SELECT id FROM user WHERE id=(?) AND password=(?)", (user_id, self.hash_pass(password)))
        except sqlite3.DatabaseError as er:
            self.prer(er)
            return None
        return cur.fetchone()

    def handling_action(self, cur, ch_user_id):
        """password request"""
        print('"{0}", please enter your password:'.format(self.name))
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
        """add new user, if not found name"""
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
                    with self.connect:
                        cur.execute("INSERT INTO user (name, password, full) VALUES (?,?,?)", (name, self.hash_pass(password), fullname))
                except sqlite3.DatabaseError as er:
                    print('Incorrect information, change data')
                    continue
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
        """parser for user command"""
        command, arg = get_command(command)
        if command not in self.COMMANDS.keys():
            return None
        result = self.COMMANDS[command]['command'](arg)
        return result

    def command_help(self, arg=None):
        """callback for .help command"""
        if arg:
            s = '.' + arg
            result = self.COMMANDS.get(s)
            if result:
                print("'{0}'\t{1}".format(s,result['full']))    
            else:
                print('not found, use ".help"')
        else:
            for key, item in self.COMMANDS.items():
                print("{0:.<30}{1}".format(key, item['desc']))
        return 'help'

    def command_exit(self, arg=None):
        # pass
        return 0

    def command_chname(self, arg=None):
        """change user name"""
        cur = self.connect.cursor()
        while(True):
            name = input("You login:")
            fullname = input("You full name (optional):")
            try:
                if name == '':
                    raise IncorrectDbData()
                with self.connect:
                    cur.execute("UPDATE user SET name=(?), full=(?) WHERE id=(?)", (name, fullname, self.user_id))
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                print('Incorrect information, change data')
                e = input('Do you wand exit from name update [N/y]?')
                if e in ('y', 'Y'):
                    break
                continue
            self.name = name
            print("You name updated successfully")
            break
        cur.close()
        return 'chname'

    def command_chpassword(self, arg=None):
        """change user password"""
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
                        with self.connect:
                            cur.execute("UPDATE user SET password=(?) WHERE id=(?)", (self.hash_pass(password1), self.user_id))
                else:
                    raise IncorrectDbData()
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                print('Incorrect information, please change data')
                e = input('Do you wand exit from password update [N/y]?')
                if e in ('y', 'Y'):
                    break
                continue
            self.password = password1
            print("You password updated successfully")
            break
        cur.close()
        return 'chpassword'

    def command_en(self, text):
        """en-ru translate"""
        print(self.command_enru(text, 'en'))
        return 'en'
    def command_ru(self, text):
        """ru-en translate"""
        print(self.command_enru(text, 'ru'))
        return 'ru'
    def command_enru(self, text, tr_type):
        """translate, only with online"""
        if not self.online:
            return "Offline, please test connect with '.connect' command"
        result = get_translate(text, tr_type)
        if not result or result['code'] != 200:
            self.command_connect()
            return "Error, not foud translate"
        return result['text']

    def command_list(self, pattern=None):
        """print user dictionary"""
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
                with self.connect:
                    translate_id = self.command_add_kinds(cur, en, ru)
            except DublicationDbData:
                print('Words already contained in database. For search use ".list {0}"'.format(en))
                break
            except (sqlite3.DatabaseError, IncorrectDbData) as er:
                self.prer(er)
                print('Incorrect information, change data')
                ent = input('Do you wand enter new words [Y/n]?')
                if ent in ('n', 'N'):
                    break
                continue
            # may be use "else"
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
        if not cur.fetchone():
            # insert in to tables
            sql_list1 = "INSERT INTO `term` (`token`, `en`) VALUES ((?), (?))"
            cur.execute(sql_list1, (token, prepare_str(en)))
        cur.execute("SELECT `id` FROM `translate` WHERE `term`=(?) AND `user_id`=(?)", (token, self.user_id))
        if cur.fetchone(): raise DublicationDbData()
        # add translate row
        sql_list2 = "INSERT INTO `translate` (`term`, `user_id`, `rus`) VALUES (?, ?, ?)"
        cur.execute(sql_list2, (token, self.user_id, prepare_str(ru)))
        translate_id = cur.lastrowid
        # add progress row
        sql_list3 = "INSERT INTO `progress` (`translate_id`) VALUES (?)"
        cur.execute(sql_list3, (translate_id,))
        return translate_id

    def command_export(self, arg=None):
        """export all user dictionary in CSV file"""
        global EXPORT_NAME, DEBUG
        if arg:
            export_name = arg
        else:
            d = datetime.date.today()
            export_name = EXPORT_NAME + d.strftime("%Y_%m_%d") + ".csv"
        try:
            cur = self.connect.cursor()
            writer_csv = csv.writer(open(export_name, 'w', newline='', encoding='utf-8'), dialect='excel', delimiter=';', quoting=csv.QUOTE_ALL)
            writer_csv.writerow(['ENGLISH','RUSSIAN'])
            sql_list = "SELECT `term`.`en`, `translate`.`rus` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) WHERE `translate`.`user_id`=(?) ORDER BY `term`.`en`, `translate`.`rus`"
            cur.execute(sql_list, (self.user_id,))
            for result in cur.fetchall():
                writer_csv.writerow(result)
        except Exception as er:
            self.prer(er)
            print("Export error")
        else:
            print("Export finished successfully to file: {0}".format(export_name))
        cur.close()
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
            with self.connect:
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
            self.prer(er)
            print('Record not found for current user.')
        except (TypeError, ValueError, sqlite3.DatabaseError) as er:
            self.prer(er)
            print("Error, use '.edit ID' (ID is numerical)")
        else:
            print('Successfully update')
        cur.close()
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
            with self.connect:
                for rec in id_for_del:
                    # delete translate
                    cur.execute("DELETE FROM `translate` WHERE `id`=(?)", (rec[0],))
                    # delete progress
                    cur.execute("DELETE FROM `progress` WHERE `translate_id`=(?)", (rec[0],))
                    # del from term if it needed
                    cur.execute("SELECT `term` FROM `translate` WHERE `term`=(?) LIMIT 1", (rec[1],))
                    if not cur.fetchone():
                        cur.execute("DELETE FROM `term` WHERE `token`=(?)", (rec[1],))
        except IncorrectDbData as er:
            self.prer(er)
            print('Record not found for current user.')
        except (sqlite3.DatabaseError, TypeError) as er:
            self.prer(er)
            print("Error, use '.delete [ID or pattern]' (ID is numerical)")
        else:
            print('Successfully update')
        cur.close()
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
        """search user pattern"""
        sql_str = "SELECT `term`.`en`, `translate`.`rus`, `term`.`token`, `translate`.`id` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) "
        if by_pattern:
            pattern = for_search + '%' 
            sql_str += "WHERE `term`.`en` LIKE (?) AND `user_id`=(?) ORDER BY `translate`.`id`"
        else:
            pattern = for_search
            sql_str += "WHERE `translate`.`id`=(?) AND `user_id`=(?) ORDER BY `translate`.`id`"
        cur.execute(sql_str, (pattern, self.user_id))
        return cur.fetchall()

    def command_import(self, import_name):
        """import user dict to CSV"""
        start = False
        cur = self.connect.cursor()
        try:
            read_csv = csv.reader(open(import_name, newline='', encoding='utf-8'), dialect='excel', delimiter=';', quoting=csv.QUOTE_ALL)
            with self.connect:
                for row in read_csv:
                    if not start:
                        start = True
                        continue
                    if len(row) < 2: continue
                    en = row[0]
                    ru = row[1]
                    # check term
                    token = hashlib.md5(bytes(prepare_str(en), 'utf-8')).hexdigest()
                    # check translate
                    cur.execute("SELECT `term` FROM `translate` WHERE `user_id`=(?) AND `term`=(?)", (self.user_id, token))
                    if not cur.fetchone():
                        # check term
                        cur.execute("SELECT `token` FROM `term` WHERE `token`=(?)", (token,))
                        if not cur.fetchone():
                            cur.execute("INSERT INTO `term` (`token`, `en`) VALUES ((?), (?))", (token, prepare_str(en)))
                        cur.execute("INSERT INTO `translate` (term,user_id,rus) VALUES (?,?,?)", (token, self.user_id, prepare_str(ru)))
                        translate_id = cur.lastrowid
                        cur.execute("INSERT INTO `progress` (`translate_id`) VALUES (?)", (translate_id,))
                        print("Added: {0}".format(en))
                    else:
                        print("Dublicate record: {0}".format(en))
        except sqlite3.DatabaseError as er:
            self.prer(er)
            print("DB error for {0}".format(en))
        except (TypeError, IOError) as er:
            self.prer(er)
            print("Please write '.import import_file.csv'")
        cur.close()
        return 'import'

    def command_testen(self, arg):
        self.command_test(arg, 0)
        return 'test-en'
    def command_testru(self, arg):
        self.command_test(arg, 1)
        return 'test-ru'
    def command_testmix(self, arg):
        self.command_test(arg, 2)
        return 'test-mix'

    def command_test(self, arg=None, type_test=0):
        """start user test"""
        cur = self.connect.cursor()
        created = datetime.datetime.now()
        name = ''
        try:
            arg = int(arg) if arg else self.ctest
        except (TypeError, ValueError) as e:
            arg = self.ctest
        # start test
        types_test = ('en-ru', 'ru-en', 'mix')
        print("Start test, type: '{0}', count: {1}".format(types_test[type_test], arg))
        try:
            with self.connect:
                # insert `test`
                cur.execute("INSERT INTO `test` (`user_id`, `name`, `created`) VALUES (?,?,?)", (self.user_id, types_test[type_test], created))
                test_id = cur.lastrowid
                alreadyq, to_save, progress = [], [], []
                for i in range(1, arg+1):
                    # 0-en, 1-ru, 2-mix
                    question, answer, translate_id  = self.gen_question(cur, type_test, alreadyq)
                    if question is None:
                        print("too few words")
                        break
                    alreadyq.append(str(translate_id))
                    print('\nQuestion {0}: {1}'.format(i,question))
                    enter = input('translate: ')
                    # check error
                    er = False if check_ans(answer, enter) else True
                    result_row = {"test_id": test_id, "num": i, "question": question, 'answer': answer, 'enter': enter, 'error': er}
                    to_save.append(result_row)
                    progress_error = 1 if er else 0
                    progress.append({'translate_id': translate_id, 'error': progress_error})
                # save results
                cur.executemany("INSERT INTO `result` (`test_id`,`number`,`question`,`answer`,`enter`,`error`) VALUES (:test_id, :num, :question, :answer, :enter, :error)", to_save)
                # update test
                cur.execute("UPDATE `test` SET `finished`=(?) WHERE `id`=(?)", (datetime.datetime.now(), test_id))
                # update progress
                cur.executemany("UPDATE `progress` SET `all`=`all`+1, `error`=`error`+:error WHERE `translate_id`=:translate_id", progress)
        except sqlite3.DatabaseError as er:
            self.prer(er)
            print("Error")
        else:
            print("Test successfully finished")
            self.print_test_result(to_save)
        cur.close()

    def print_test_result(self, tests):
        """print test info"""
        right, error = 0, 0
        print("*******YOUR ERRORS********")
        for q in tests:
            if q['error']:
                error += 1
                print("\nQ#{0}: {1}\n[correcnt] {2}\n[you] {3}".format(q['num'],q['question'],q['answer'],q['enter']))
            else:
                right += 1
        print("**************************")
        print("\nResult: {0} error(s) from {1}".format(error,(right + error)))

    def gen_question(self, cur, type_test, alreadyq):
        sql_list = "SELECT `translate`.`id`, `term`.`en`, `translate`.`rus` FROM `translate` LEFT JOIN `term` ON (`translate`.`term`=`term`.`token`) WHERE `translate`.`user_id`=" + str(self.user_id) + " AND (`translate`.`id` NOT IN (" + ", ".join(alreadyq) + "))"
        cur.execute(sql_list)
        for_search = cur.fetchall()
        if not for_search:
            return None, None, None
        row = for_search[random.randint(0,len(for_search)-1)]
        # 0 => en, 1 => ru, 2 => mix
        translate_id = row[0]
        if type_test == 0:
            question, answer = row[1], row[2]
        elif type_test == 1:
            question, answer = row[2], row[1]
        else:
            i = random.randint(1,2)
            j = 1 if i == 2 else 2
            question, answer = row[i], row[j]
        return question, answer, translate_id

    def command_tets(self, arg=None):
        pass

    def command_testinfo(self, test_id=None):
        pass

