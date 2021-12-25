from replit import db
from config import KEYS
from discord.guild import *
from tools import getkey


# Role methods

# Recognizers

async def is_unique(rle: str, gld: Guild):
    """
    Determines if given role has more than one member.
    :param rle: string name of role
    :param gld: Guild object containing role
    :return: True iff role has 0 or 1 members, False otherwise
    """
    role_obj = await get(gld, rle)  # type: Role
    if role_obj is None:
        return False
    else:
        return len(role_obj.members) <= 1


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
                it = iter(table[mode][rle])
                # next(it)
                hero = next(it)
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode}]")
            elif rle == 'Time Played':
                hero = getkey(table[mode][rle])
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode}]")

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK]     # Table of battlenet's competitive ranks

    for rle in table:  # type: str
        roles.add(f"{rle.capitalize()}-{table[rle]}")

    return roles


# Updaters

async def add(gld: Guild, rle: str):
    role_obj = await gld.create_role(name=rle)
    return role_obj


async def get(gld: Guild, rle: str):
    roles = await gld.fetch_roles()
    for r in roles:
        if str(r) == rle:
            return r
    return None


async def update(gld: Guild, disc: str, bnet: str):
    print(f"Updating roles for {disc}[{bnet}]...")

    mmbr = await gld.fetch_member(db[KEYS.MMBR][disc][KEYS.ID])     # type: Member

    print(f"Member fetched: {str(mmbr)} ({mmbr.id})")

    roles = get_bnet_roles(disc, bnet)                  # Roles battlenet should have
    current_roles = set(str(r) for r in mmbr.roles)     # Roles discord user currently has
    to_add = roles.difference(current_roles)            # Roles user should have minus roles discord thinks they have

    print(f"Roles in to_add: {to_add}")
    input("ENTER: ")

    # To get roles to remove, first we get roles currently associated with battlenet which have no correlation
    # to actual roles held. Taking the union of this with roles the user SHOULD have we get the roles
    # that the user SHOULD have plus the roles that they already have. Taking the intersection of this with
    # roles that specifically Discord knows they have gives us the roles that the user definitely has in Discord
    # that are also controlled by the bot (ignoring roles they have that aren't this bot's). Then, taking
    # the difference of this set with roles they SHOULD have, gives us the roles that they have, that are
    # controlled by the bot, that they now should NOT have, thus giving us to_remove

    # All roles associated with battlenet, no correlation to roles held
    bnet_roles = set(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE])
    all_roles = bnet_roles.union(roles)  # All roles the user currently or previously associated with battlenet

    print(f"Roles in all_roles: {all_roles}")
    input("ENTER: ")

    # roles_held is all roles that the bot could have given the user that they DO have
    roles_held = all_roles.intersection(current_roles)

    print(f"Roles in roles_held: {roles_held}")
    input("ENTER: ")

    # Thus, to_remove is all the roles bot given roles minus the ones that the user SHOULD have
    to_remove = roles_held.difference(roles)

    print(f"Roles in to_remove: {to_remove}")
    input("ENTER: ")

    for role in to_add:
        role_obj = await get(gld, role)
        if role_obj is None:
            role_obj = await add(gld, role)

        db[KEYS.ROLE][role] = role_obj.id
        await mmbr.add_roles(role_obj)

    for role in to_remove:
        role_obj = gld.get_role(db[KEYS.ROLE][role])    # type: Role

        if await is_unique(role, gld):
            await role_obj.delete()
            del db[KEYS.ROLE][role]

    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(roles)
