from replit import db
from config import KEYS
from os import system
from unidecode import unidecode
from json import load


def data_categories():
    if not system("./get/category > categories"):
        categ_id = {}
        with open("categories", "r") as infile:
            lines = infile.readlines()

        for line in lines:
            line = line.strip('\n')
            # Only read categories that start with data-id
            if not line.startswith("0x"):
                continue
            else:
                _id, name = line.split('|')
                name = unidecode(name)
                categ_id[_id] = name

        system("rm -f categories")
        return categ_id
    else:
        raise ValueError("UNIX ERROR")


def init():
    db[KEYS.MMBR] = {}
    db[KEYS.ROLE] = {}
    db[KEYS.BNET] = []
    with open("categories.json", "r") as infile:
        db[KEYS.CTG] = load(infile)


def clear():
    for key in db.keys():
        del db[key]


def refresh():
    clear()
    init()
