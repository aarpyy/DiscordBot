from replit import db
from config import *


def remove_user(user):
    if user in db:
        # Iterate through all user's battletags, removing all that are not shared by another discord user
        map(remove_bnet, db[user][key_all])

        # Remove user from list of all discords
        del db[user]
        db[key_dsc].remove(user)
        return "{0} successfully removed!".format(user)
    else:
        return "{0} not a registered user".format(user)


def remove_bnet(bnet):
    if bnet in db[key_bn]:
        db[key_bn].remove(bnet)
    if bnet in db:
        del db[bnet]
    return True
