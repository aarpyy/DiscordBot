from replit import db
from config import KEYS, data_categories
import retrieve
import asyncio
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
    n_units = 0
    while t:
        t, r = divmod(t, 60)
        time.append(r)
        n_units += 1

    units = {1: 's', 2: 'm', 3: 'h', 4: 'd', 5: 'y'}
    if n_units in units:
        return f"{time.pop()}{units[n_units]}"
    else:
        raise ValueError("Invalid time given") from None


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

    # For each stat associated with battlenet, add that stat if it is an important one
    for mode in table:
        for rle in table[mode]:
            if rle == 'Win Percentage':
                hero = get_keys(table[mode][rle])
                roles.add(f"{hero}–{table[mode][rle][hero]}%W [{mode}]")
            elif rle == 'Time Played':
                hero = get_keys(table[mode][rle])
                roles.add(f"{hero}–{seconds_to_time(table[mode][rle][hero])} [{mode}]")

    table = db[bnet][KEYS.RANK]

    for rle in table:   # type: str
        roles.add(f"{rle.capitalize()} - {table[rle]}")

    return roles


async def update(gld: Guild, disc: str):
    mmbr = gld.get_member_named(disc)   # type: Member

    # Remove all roles from user that are in list of bot-created roles
    for rle in db[disc][KEYS.ROLE]:

        print(f"Removing role :{rle}")
        role_obj = gld.get_role(db[KEYS.ROLE][rle])     # type: Role

        await mmbr.remove_roles(role_obj, reason="Role refresh")

        print(f"Members with this role after removal: {', '.join(str(e) for e in role_obj.members)}")

        # If current member is the only member who has this role, remove it
        if not len(role_obj.members):
            await role_obj.delete()
            del db[KEYS.ROLE][rle]

    db[disc][KEYS.ROLE] = []

    # All bot given roles are removed, now add all back
    await init(gld, disc)


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
