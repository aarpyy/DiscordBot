from replit import db
from config import KEYS


def member(user):
    if user in db:
        # Iterate through all user's battletags, removing all that are not shared by another discord user
        map(battlenet, db[user][KEYS.ALL])

        # Remove user from list of all discords
        del db[user]
        db[KEYS.DSC].remove(user)
        return "{0} successfully removed!".format(user)
    else:
        return "{0} not a registered user".format(user)


def battlenet(bnet):
    if bnet in db[KEYS.BNT]:
        db[KEYS.BNT].remove(bnet)
    if bnet in db:
        del db[bnet]
    return True
