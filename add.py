import request
import remove
from config import KEYS
from discord.utils import get
from replit import db


def battlenet(user, bnet):
    
    # If user in in database and battlenet also is but battlenet isn't linked than this user can't access. If it is linked then return. If user in db and battlnet not in then everything is fine. If user is not in db but battlenet is, then battlenet is registered to another user.
    if user in db:
        if bnet in db:
            if bnet not in db[user][KEYS.ALL]:
                raise NameError(f"{bnet} linked to another account")
            else: 
                return
        else:
            db[user][KEYS.ALL].append(bnet)
    elif bnet in db:
        raise NameError(f"{bnet} linked to another account")
    else:
        # If not linked discord, add it now in case bnet needs to be removed from this user
        db[user] = {KEYS.PRM: bnet, KEYS.ALL: [bnet]}
        db[KEYS.DSC].append(user)

    # Load bnet information in table
    request.main(bnet)

    # If player_request was unable to load time played, then this user is either private or DNE
    if not db[bnet][KEYS.TPL]:
        # Delete data associated with battletag if it is inaccessible
        remove.battlenet(bnet)
        raise ValueError(bnet, "is either private or does not exist")


async def role(guild, name):
    if name not in db[KEYS.RLE]:
        print("Creating {0} as a role...".format(name))
        await guild.create_role(name=name)
        role_obj = get(guild.roles, name=name)
        db[KEYS.RLE][name] = role_obj.id
        return role_obj
    return get(guild.roles, name=name)
