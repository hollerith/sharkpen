import os
import sqlite3

DBPATH = os.path.join(os.path.dirname(__file__), 'test.db')

def db_connect(db_path=DBPATH):
    con = sqlite3.connect(db_path)
    return con

class Object(dict):
    def __getattr__(self, name):
        return self[name]
