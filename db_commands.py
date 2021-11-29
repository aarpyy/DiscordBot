from replit import db
from config import KEYS as k
from functools import reduce


def clear():
    try:
        for key in db:
            if key not in k.const:
                del db[key]
        db[k.BNET] = []
        db[k.DSC] = []
    except KeyError:
        return "An error occurred"
    else:
        return "Database cleared!"


def get(*keys):
    try:
        return reduce(lambda r, c: r[c], keys, db)
    except KeyError:
        return "One or more of the keys given does not exist"


def add(value, *keys):
    keys = list(keys)
    final = keys.pop(-1)
    try:
        _dict = reduce(lambda r, c: r[c], keys, db)
    except KeyError:
        return "One or more of the keys given does not exist"
    else:
        _dict[final] = value
        return "{0} added to database".format(value)


def addint(value, *keys):
    keys = list(keys)
    final = keys.pop(-1)
    try:
        _dict = reduce(lambda r, c: r[c], keys, db)
    except KeyError:
        return "One or more of the keys given does not exist"
    else:
        _dict[final] = int(value)
        return "{0} added to database".format(value)


def remove(key, *keys):
    try:
        _dict = reduce(lambda r, c: r[c], keys, db)
    except KeyError:
        return "One or more of the keys given does not exist"
    else:
        del _dict[key]
        return "{0} successfully deleted".format(key)


def admin(value):
    db[k.ADM].append(value)
    return "{0} successfully added as a database administrator".format(value)
