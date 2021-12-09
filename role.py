from replit import db
from config import KEYS, data_categories
import retrieve
from discord.guild import *


def get_keys(d: dict, n: int = 1):
    it = iter(d)
    if n == 1:
        return next(it)
    else:
        return tuple(map(lambda x: next(it), range(n)))


# Converts time (in seconds) into a string to display time
def seconds_to_time(t):
    time = []
    while t:
        t, r = divmod(t, 60)
        time.insert(0, r)

    if len(time) == 4:
        return "{0}d, {1}h, {2}m, {3}s".format(*time)
    elif len(time) == 3:
        return "{0}h, {1}m, {2}s".format(*time)
    elif len(time) == 2:
        return "{0}m, {1}s".format(*time)
    elif len(time) == 1:
        return "{0}s".format(*time)
    else:
        return ':'.join(str(e) for e in time)


# Role methods

# Refresh all roles for all members of a guild
async def refresh(gld: Guild):
    for mmbr in gld.members:
        await update(gld, mmbr)
    return True


async def remove(rle: Role, reason=None):
    if rle in db[KEYS.ROLE]:
        await rle.delete(reason=reason)
        db[KEYS.ROLE].remove(rle)
    else:
        raise KeyError(f"{rle} not in database") from None


async def add(gld, rle):
    if rle not in db[KEYS.ROLE]:
        role_obj = await gld.create_role(name=rle)
        db[KEYS.ROLE][rle] = int(role_obj.id)
    else:
        role_obj = gld.get_role(db[KEYS.ROLE][rle])
    return role_obj


def get(bnet):
    roles = set()
    table = db[bnet][KEYS.STAT]
    # For each stat associated with battlenet, add that stat
    for mode in table:
        for rle in table[mode]:
            if rle == 'Win Percentage':
                hero = get_keys(table[mode][rle])
                roles.add(f"{hero}–{table[mode][rle][hero]}%W [{mode}]")
            elif rle == 'Time Played':
                hero = get_keys(table[mode][rle])
                roles.add(f"{hero}–{seconds_to_time(table[mode][rle][hero])} [{mode}]")

    return roles


async def init(gld, mmbr):

    roles = set()

    # For each battlenet linked with user,
    for bnet in db[mmbr][KEYS.ALL]:
        roles.update(get(bnet))

    mmbr = gld.get_member_named(mmbr)
    for rle in roles:
        # Get role object, either by creating it or by getting it from dict of role: role_id
        role_obj = await add(gld, rle)

        # If role not added to member, add it
        if mmbr not in role_obj.members:
            await mmbr.add_roles(role_obj)
            db[str(mmbr)][KEYS.ROLE].append(rle)

        if rle not in db[KEYS.ROLE]:
            db[KEYS.ROLE][rle] = int(role_obj.id)


async def update(gld: Guild, disc: str):
    mmbr = gld.get_member_named(disc)

    # Remove all roles from user that are in list of bot-created roles
    for rle in db[disc][KEYS.ROLE]:
        role_obj = gld.get_role(db[KEYS.ROLE][rle])

        # If current member is the only member who has this role, remove it
        if len(role_obj.members) <= 1:
            role_obj.delete()
            db[KEYS.ROLE].remove(rle)
        
        


    db[disc][KEYS.ROLE] = []

    # All bot given roles are removed, now add all back
    await init(gld, disc)

