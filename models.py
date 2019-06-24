from __future__ import absolute_import, print_function

from decimal import Decimal
from datetime import datetime

from pony.converting import str2datetime
from pony.orm import *

db = Database("sqlite", "/tmp/test.sqlite", create_db=True)

class User(db.Entity):
    username = Required(str, unique=True)
    password = Required(str)
    sites = Set("Site")

class Site(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    color = Optional(str)
    notes = Optional(str)
    targets = Optional(str)
    owner = Required(User)

class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)

class Target(db.Entity):
    id = PrimaryKey(int, auto=True)
    hostname = Optional(str)
    comments = Optional(str)

"""
class Task(db.Entity):
    id = PrimaryKey(int, auto=True)
    category = Required(Category)
    priority = Optional(int)
    schedule = Optional(str)
    repeated = Optional(str)
    payload  = Optional(str)
"""

db.generate_mapping(create_tables=True)

with db_session:
    if User.select().first() is None:
        admin = User(username='admin', password='admin')

    if Site.select().first() is None:
        site = Site(name='Xen', color='red', notes='Endgame', targets='10.10.10.14,10.10.10.15',owner=admin)

    if Category.select().first() is None:
        category = Category(name='Paths')
        category = Category(name='Credentials')
        category = Category(name='Injection')
        category = Category(name='Enumeration')
