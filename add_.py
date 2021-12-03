import request
import remove
from config import KEYS
from discord.utils import get
from replit import db


def battlenet(member, bnet, platform):
    if bnet in db:
        # If user in in database and battlenet also is but battlenet isn't linked than this user can't access.
        if bnet not in db[member][KEYS.ALL]:
            raise NameError(f"{bnet} is already linked to another account!")
        else:
            # If it is linked then return. If user in db and battlnet not in then everything is fine.
            return

    # At this point, user is in database with primary and all values and in list of all discords

    # Load bnet information in table - if the battlenet is not in list of all battlenets it gets added here
    try:
        rank, stats = request.main(request.search_url(platform)(bnet))
    except ValueError as src:
        # If player_request was unable to load time played, then this user is either private or DNE

        # Delete data associated with battletag if it is inaccessible
        remove.battlenet(bnet)
        raise ValueError(bnet, "is either private or does not exist") from src
    else:
        db[bnet] = {KEYS.RANK: rank, KEYS.STAT: stats, KEYS.PLTFRM: platform}
        db[KEYS.BNET].append(bnet)
        db[member][KEYS.ALL].append(bnet)
        if db[member][KEYS.PRIM] is None:
            db[member][KEYS.PRIM] = bnet


async def role(guild, name):
    if name not in db[KEYS.ROLE]:
        print("Creating {0} as a role...".format(name))
        await guild.create_role(name=name)

        # Get ID and add to table of roles
        role_obj = get(guild.roles, name=name)
        db[KEYS.ROLE][name] = role_obj.id
        return role_obj
    return get(guild.roles, name=name)
