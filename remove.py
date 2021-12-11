from replit import db
from config import KEYS


def battlenet(bnet, disc):
    db[KEYS.BNET].remove(bnet)
    del db[KEYS.MMBR][disc][KEYS.ALL][bnet]

    return "Successfully removed {0}".format(bnet)
