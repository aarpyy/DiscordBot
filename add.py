import request
from remove import remove_bnet
from config import KEYS as k
from discord.utils import get
from replit import db


def battlenet(user, bnet):
    # If already added as a battlenet, don't do anything
    if user in db and bnet in db[user][k.ALL]:
        return

    # If the account already loaded and not for this user, don't allow them to link
    if bnet in db and bnet not in db[user][k.ALL]:
        raise NameError("{0} linked to another account".format(bnet))

    # Load bnet information in table
    request.main(bnet)

    # If player_request was unable to load time played, then this user is either private or DNE
    if not db[bnet][k.TPL]:
        # Delete data associated with battletag if it is inaccessible
        remove_bnet(bnet)
        raise ValueError(bnet, "is either private or does not exist")
    elif user in db:
        db[user][k.ALL].append(bnet)
    else:
        db[user] = {k.PRM: bnet, k.ALL: [bnet]}

    db[k.BNT].append(bnet)


async def role(guild, name):
    if name not in db[k.RLE]:
        print("Creating {0} as a role...".format(name))
        await guild.create_role(name=name)
    return get(guild.roles, name=name)
