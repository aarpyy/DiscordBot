from replit import db
from config import KEYS


def member(user):
    if user in db:
        # Iterate through all user's battletags, removing all that are not shared by another discord user
        for bnet in db[user][KEYS.ALL]:
            del db[bnet]
            db[KEYS.BNET].remove(bnet)

        # Remove user from list of all discords
        del db[user]
        db[KEYS.MMBR].remove(user)
        return "{0} successfully removed!".format(user)
    else:
        return "{0} not a registered user".format(user)


def battlenet(bnet):
    if bnet in db[KEYS.BNET]:
        db[KEYS.BNET].remove(bnet)
    if bnet in db:
        del db[bnet]
    for user in db[KEYS.MMBR]:
        if bnet in db[user][KEYS.ALL]:
            db[user][KEYS.ALL].remove(bnet)
        if bnet == db[user][KEYS.PRIM]:
            if len(db[user][KEYS.ALL]) > 0:
                db[user][KEYS.PRIM] = db[user][KEYS.ALL][0]
            else:
                del db[user]
                db[KEYS.MMBR].remove(user)
    return "Successfully removed {0}".format(bnet)


def role(bnet, rl):
    pass
