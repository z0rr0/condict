#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib, getpass
DEBUG = False

class BaseConDict(object):
    """Base Console Dictionary class"""
    def __init__(self, name, dbfile):
        self.connect = sqlite3.connect(dbfile)
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
    def __init__(self, name, dbfile):
        super().__init__(name, dbfile)       
        self.__pcounter = 3
        self.user_id = self.get_user()

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

    def hash_pass(self, password):
        result = bytes(password.strip().lower(), 'utf-8')
        return hashlib.sha1(result).hexdigest()

    def check_name(self, cur):
        try:
            cur.execute("SELECT id FROM user WHERE name=(?)", (self.name,))
        except sqlite3.DatabaseError as er:
            return None
        return cur.fetchone()

    def check_password(self, cur, user_id):
        try:
            cur.execute("SELECT id FROM user WHERE id=(?) AND password=(?)", (user_id, self.hash_pass(self.password)))
        except sqlite3.DatabaseError as er:
            return None
        return cur.fetchone()

    def handling_action(self, cur, ch_user_id):
        print('"{0}" please enter your password:'.format(self.name))
        while(self.__pcounter > 0):
            self.password = input("Password:") if DEBUG else getpass.getpass()
            user_id = self.check_password(cur, ch_user_id)
            if user_id:
                return user_id[0]
            else:
                action = input('Invalid password, there are actions "Exit"/"Press password again" [e/P]:')
                if action in ('', 'P', 'p'):
                    self.__pcounter -= 1
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
                fullname = input("You full name:")
                password = input("Password:") if DEBUG else getpass.getpass()
                transaction_ok = False
                try:
                    cur.execute("INSERT INTO user (name, password, full) VALUES (?,?,?)", (name, self.hash_pass(password), fullname))
                except sqlite3.DatabaseError as er:
                    print(er)
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
