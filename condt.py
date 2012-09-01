#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib

class Condt():
    """Condt - base class for ConDict"""


    def __init__(self, name, password, dbfile):
        self.name = name
        self.password = password
        self.connect = sqlite3.connect(dbfile)
        self.user_id = None
        if self.get_user() != 0:
            self.handling_action()
        print(self.user_id)

    def __repr__(self):
        return "<ConDict object for {0}>".format(self.name)

    def __str__(self):
        return "<ConDict object for {0}>".format(self.name)

    def __del__(self):
        self.connect.close()

    def get_user(self):
        sqlstr="SELECT id FROM user WHERE name=(?) AND password=(?)"
        cur = self.connect.cursor()
        try:
            cur.execute(sqlstr, (self.name, self.hash_pass(self.password)))
            result = cur.fetchone()
            if result:
                self.user_id = result[0]
            else:
                return 1
        except (sqlite3.DatabaseError, TypeError)  as er:
            print('error')
        cur.close()
        return 0

    def hash_pass(self, password):
        return password
    def hash_pass1(self, password):
        result = bytes(password.strip().lower(), 'utf-8')
        return hashlib.sha1(result).hexdigest()

    def handling_action(self):
        while(True):
            action = input('Sorry, not found user, there are actions "Add new user"/"Press password again" [a/P]:')
            if action in ('', 'P', 'p'):
                print('press')
                break
            elif action in ('a', 'A'):
                print('add', self.name)
                break
            else:
                print('select an option...')
        print('ok')
