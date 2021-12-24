from replit import db
from config import KEYS
from discord.guild import *


# Role methods

# Recognizers

def is_unique(rle: str, gld: Guild):
    """
    Determines if given role has more than one member.
    :param rle: string name of role
    :param gld: Guild object containing role
    :return: True iff role has 0 or 1 members, False otherwise
    """
    if rle in db[KEYS.ROLE]:
        role_obj = gld.get_role(db[KEYS.ROLE][rle])
        if role_obj is None:
            return False
        else:
            return len(role_obj.members) <= 1
    else:
        return False


# Accessors

def get_bnet_roles(disc: str, bnet: str):
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles
    mode_short = {'quickplay': 'qp', 'competitive': 'comp'}

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT]     # Table of battlenet's statistics

    # For each stat associated with battlenet, add that stat if it is an important one
    for mode in table:
        for rle in table[mode]:
            # Heroes organized in descending stat value already so getting first hero for both of these
            # gets the hero with the best stats
            if rle == 'Win Percentage':
                hero = next(iter(table[mode][rle]))
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode}]")
            elif rle == 'Time Played':
                hero = next(iter(table[mode][rle]))
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode}]")

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK]     # Table of battlenet's competitive ranks

    for rle in table:  # type: str
        roles.add(f"{rle.capitalize()}-{table[rle]}")

    return roles


# Updaters

async def remove(rle: Role, reason=None):
    await rle.delete(reason=reason)
    db[KEYS.ROLE].remove(str(rle))


async def add(gld: Guild, mmbr: Member, rle: str):
    role_obj = await gld.create_role(name=rle)
    db[KEYS.ROLE][rle] = role_obj.id
    await mmbr.add_roles(role_obj)


async def update(gld: Guild, disc: str, bnet: str):
    mmbr = await gld.fetch_member(db[KEYS.MMBR][disc][KEYS.ID])     # type: Member
    roles = get_bnet_roles(disc, bnet)

    current_roles = set(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE])

    to_add = roles.difference(current_roles)
    to_remove = current_roles.difference(roles)

    for role in to_add:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE].append(role)
        if role in db[KEYS.ROLE]:   # If someone else has this role, just use same role object
            await mmbr.add_roles(gld.get_role(db[KEYS.ROLE][role]))
        else:
            await add(gld, mmbr, role)

    for role in to_remove:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE].remove(role)
        role_obj = gld.get_role(db[KEYS.ROLE][role])    # type: Role
        if is_unique(role, gld):
            await remove(role_obj)
        await mmbr.remove_roles(role_obj)
