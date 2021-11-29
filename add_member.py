import request
from remove import remove_bnet
from config import *
from replit import db


def add(user, bnet):
    # If already added as a battlenet, don't do anything
    if user in db and bnet in db[user][key_all]:
        return

    # If the account already loaded and not for this user, don't allow them to link
    if bnet in db and bnet not in db[user][key_all]:
        raise NameError("{0} linked to another account".format(bnet))

    # Load bnet information in table
    request.main(bnet)

    # If player_request was unable to load time played, then this user is either private or DNE
    if not db[bnet][key_t]:
        # Delete data associated with battletag if it is inaccessible
        remove_bnet(bnet)
        raise ValueError(bnet, "is either private or does not exist")
    elif user in db:
        db[user][key_all].append(bnet)
    else:
        db[user] = {key_pr: bnet, key_all: [bnet]}

    db[key_bn].append(bnet)
