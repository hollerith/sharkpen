import json

from bottle import install, debug, route, run, template, request, response, redirect, abort, static_file
from utils import db_connect, DBPATH

from pony.orm.integration.bottle_plugin import PonyPlugin
from pony.orm import *
install(PonyPlugin())

from models import User, Site
import inspect

import requests

@route('')
def do_proxy():
    r = requests.get(request.url)
    return r.content

if __name__ == "__main__":
    debug(True)
    run(port=9011)