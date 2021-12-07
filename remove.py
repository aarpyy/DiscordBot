from replit import db
from config import KEYS


def battlenet(bnet, disc=None):
    db[KEYS.BNET].remove(bnet)
    del db[bnet]

    if disc in db:
        db[disc][KEYS.ALL].remove(bnet)
    else:
        for disc in db[KEYS.MMBR]:
            if bnet in db[disc][KEYS.ALL]:
                db[disc][KEYS.ALL].remove(bnet)

    return "Successfully removed {0}".format(bnet)
