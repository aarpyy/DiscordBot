from replit import db
from config import KEYS


def init():
    db[KEYS.MMBR] = {}
    db[KEYS.ROLE] = {}
    db[KEYS.BNET] = []


def clear():
    for key in db.keys():
        del db[key]


def refresh():
    clear()
    init()
