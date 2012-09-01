#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sqlite3, hashlib

class Condt():
    """Condt - base class for ConDict"""


    def __init__(self, name, password, dbfile):
        self.name = name
        self.password = password
        self.connect = sqlite3.connect(dbfile)
        self.get_user()
        print(self.user_id)

    def __repr__(self):
        return "<ConDict object for {0}>".format(self.name)

    def __str__(self):
        return "<ConDict object for {0}>".format(self.name)

    def __del__(self):
        self.connect.close()

    def get_user(self):
        sqlstr="SELECT id FROM user WHERE name={0} AND password={1}".format(self.name, self.hash_pass(self.password))
        print(sqlstr)
        cur = self.connect.cursor()
        try:
            cur.executescript(sqlstr)
        except sqlite3.DatabaseError as er:
            print('error')
        cur.close()
        self.user_id = 2

    def hash_pass(self, password):
        result = bytes(password.strip().lower(), 'utf-8')
        return hashlib.sha1(result).hexdigest()
