from replit import db
from config import KEYS, data_categories
import retrieve
from discord import *
from discord.guild import *


def user(gld, mmbr):
    """Returns all roles held by member"""
    if isinstance(mmbr, str):
        mmbr = gld.get_member_named(mmbr)
        if mmbr is None:
            return None

    return mmbr.roles


def oberwatch_user(gld, mmbr):
    """Returns all Oberwatch specific roles held by member"""
    if isinstance(mmbr, str):
        mmbr = gld.get_member_named(mmbr)
        if mmbr is None:
            return None

    oberwatch_roles = []
    for rle in mmbr.roles:
        if str(rle) in db[KEYS.ROLE]:
            oberwatch_roles.append(rle)
    return oberwatch_roles


async def refresh(gld: Guild):
    for mmbr in gld.members:
        await update(gld, mmbr)
    return True


async def remove(*roles: Role):
    for rle in roles:
        if rle is not None:
            await rle.delete()              # Delete from discord - this should also delete from all members
            del db[KEYS.ROLE][str(rle)]     # Delete from list of all roles
            for mmbr in db[KEYS.MMBR]:      # For each member that has this role
                if rle in db[mmbr][KEYS.ROLE]:
                    # Remove role from list of their roles
                    db[mmbr][KEYS.ROLE].remove(rle)
    return True


def role_filter(rle, value):
    print(f"role: {rle}; value: {value}")
    return rle in data_categories or (rle == 'Weapon Accuracy' and value[0] in ('Hanzo', 'Widowmaker'))


async def add(gld, rle):
    if rle not in db[KEYS.ROLE]:
        role_obj = await gld.create_role(name=rle)
        db[KEYS.ROLE][rle] = role_obj.id
    else:
        role_obj = gld.get_role(db[KEYS.ROLE][rle])
    return role_obj


async def get(bnet):
    roles = set()
    table = retrieve.player_roles(bnet)
    # For each stat associated with battlenet, add that stat
    for mode in table:
        for rle in table[mode]:
            for hero in table[mode][rle]:
                if role_filter(rle, hero):
                    roles.add(f"{mode}-{rle}-{'-'.join(str(e) for e in table[mode][rle][hero])}")
                break

    return roles


async def init(gld, mmbr):

    roles = set()

    # For each battlenet linked with user,
    for bnet in db[mmbr][KEYS.ALL]:
        roles.update(await get(bnet))

    for rle in roles:
        # Get role object, either by creating it or by getting it from dict of role: role_id
        role_obj = await add(gld, rle)

        # If role not added to member, add it
        if mmbr not in role_obj.members:
            await mmbr.add_roles(role_obj)
            db[mmbr][KEYS.ROLE].add(rle)


async def update(gld: Guild, mmbr: Member):

    # Remove all roles from user that are in list of bot-created roles
    for rle in db[mmbr][KEYS.ROLE]:
        role_obj = gld.get_role(db[KEYS.ROLE][rle])

        # If current member is the only member who has this role, remove it
        if len(role_obj.members) <= 1:
            role_obj.delete()
            db[KEYS.ROLE].remove(rle)

    db[mmbr][KEYS.ROLE] = set()

    await init(gld, mmbr)

