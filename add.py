import request
import remove
from config import KEYS
from discord.utils import get
from replit import db


def battlenet(user, bnet):
    # If already added as a battlenet, don't do anything
    if user in db and bnet in db[user][KEYS.ALL]:
        return

    # If the account already loaded and not for this user, don't allow them to link
    if bnet in db and bnet not in db[user][KEYS.ALL]:
        raise NameError("{0} linked to another account".format(bnet))

    # Load bnet information in table
    request.main(bnet)

    # If player_request was unable to load time played, then this user is either private or DNE
    if not db[bnet][KEYS.TPL]:
        # Delete data associated with battletag if it is inaccessible
        remove.battlenet(bnet)
        raise ValueError(bnet, "is either private or does not exist")
    elif user in db:
        db[user][KEYS.ALL].append(bnet)
    else:
        db[user] = {KEYS.PRM: bnet, KEYS.ALL: [bnet]}

    db[KEYS.BNT].append(bnet)


async def role(guild, name):
    if name not in db[KEYS.RLE]:
        print("Creating {0} as a role...".format(name))
        await guild.create_role(name=name)
    return get(guild.roles, name=name)
