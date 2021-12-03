from discord import *
from replit import db
from config import KEYS


def members(gld: Guild):
    for mmbr in gld.members:
        if mmbr not in db:
            db[mmbr] = {KEYS.PRIM: None, KEYS.ALL: [], KEYS.ROLE: set()}
        if mmbr not in db[KEYS.MMBR]:
            db[KEYS.MMBR].add(mmbr)


def database():
    db[KEYS.MMBR] = set()
    db[KEYS.BNET] = set()
    db[KEYS.ROLE] = {}
