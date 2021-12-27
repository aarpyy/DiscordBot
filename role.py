from replit import db

from discord import Guild, Member, Role, Forbidden, HTTPException
from asyncio import sleep

from config import KEYS, bot_role_prefix
from tools import getkey

from typing import Optional, List, Set

mode_short = {"quickplay": "[qp]", "competitive": "[comp]"}
categ_short = {"Win Percentage": "W", "Time Played": ""}
categ_major = ("Win Percentage", "Time Played")


# Role methods


def get_bnet_roles(disc: str, bnet: str) -> Set[str]:
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()   # Empty set for roles

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT]     # Table of battlenet's statistics

    # For each stat associated with battlenet, add that stat if it is an important one
    for mode in table:
        for ctg in table[mode]:
            if ctg in categ_major:
                hero = getkey(table[mode][ctg])
                roles.add(f"{hero}-{table[mode][ctg][hero]}" + categ_short[ctg] + f" {mode_short.get(mode, '')}")

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK]     # Table of battlenet's competitive ranks

    for rnk in table:  # type: str
        roles.add(f"{rnk.capitalize()}-{table[rnk]}")

    for r in roles:
        r = bot_role_prefix + r

    roles.add(f"@m{bnet}")
    return roles


async def get(gld: Guild, rle: str) -> Optional[Role]:
    """
    Helper function that more sufficiently ensures that the Role is returned if it exists. First, it
    checks if the Role is already in the db, getting the Role via Role.id if true. Otherwise,
    it iterates through all Roles in Guild, attempting to match via string, returning None if no
    matches were made.

    :param gld: Guild
    :param rle: name of role
    :return: Optional[Role]
    """

    # Theoretically this will always be true, since the only arguments being passed here are roles
    # created by Oberwatch bot which are all default stored in the db
    if rle in db[KEYS.ROLE]:
        return gld.get_role(db[KEYS.ROLE][rle][KEYS.ID])
    else:
        try:
            roles = await gld.fetch_roles()     # type: List[Role]
        except HTTPException:
            return None
        else:
            for r in roles:                     # type: Role
                if str(r) == rle:
                    db[KEYS.ROLE][rle] = {KEYS.ID: r.id, KEYS.MMBR: len(r.members)}
                    return r
            return None


async def update(gld: Guild, disc: str, bnet: str) -> None:
    """
    Gives Guild Member Role objects based off of the stats retrieved from connected battlenet.

    :param gld: Guild that the discord user belongs to
    :param disc: Discord username
    :param bnet: Linked battlenet
    :raises AttributeError: If Bot lacks access to Guild
    :raises ValueError: If Discord API unable to fetch Member
    :return: None
    """
    print(f"Updating roles for {disc}[{bnet}]...")

    user_id = db[KEYS.MMBR][disc][KEYS.ID]

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        mmbr = await gld.fetch_member(user_id)  # type: Member
    except Forbidden as src:
        raise AttributeError(f"Unable to access Guild {str(gld)}") from src
    except HTTPException as src:
        raise ValueError(f"Fetching user {disc}({user_id}) failed") from src

    print(f"Member fetched: {str(mmbr)} ({mmbr.id})")

    new_roles = get_bnet_roles(disc, bnet)  # Roles battlenet should have
    current_roles = set()       # Roles discord user currently has
    for r in mmbr.roles:        # type: Role
        if r.mentionable:
            current_roles.add(f"@m{str(r)}")
        else:
            current_roles.add(str(r))

    to_add = new_roles.difference(current_roles)  # Roles user should have minus roles discord thinks they have

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
    roles_listed = set(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE])
    all_roles = roles_listed.union(new_roles)  # All roles the user currently or previously associated with battlenet

    print(f"Roles in all_roles: {all_roles}")
    input("ENTER: ")

    # roles_held is all roles that the bot could have given the user that they DO have
    current_bot_roles = all_roles.intersection(current_roles)

    print(f"Roles in roles_held: {current_bot_roles}")
    input("ENTER: ")

    # Thus, to_remove is all the roles bot given roles minus the ones that the user SHOULD have
    to_remove = current_bot_roles.difference(new_roles)

    print(f"Roles in to_remove: {to_remove}")
    input("ENTER: ")

    for role in to_add:
        if role.startswith("@m"):
            role_obj = await gld.create_role(name=role[2:], mentionable=True)
            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: 0}
        else:
            role_obj = await get(gld, role)
            if role_obj is None:
                role_obj = await gld.create_role(name=role)
                db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: 0}
            elif role not in db[KEYS.ROLE]:
                db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}

        db[KEYS.ROLE][role][KEYS.MMBR] += 1
        await mmbr.add_roles(role_obj)

    for role in to_remove:
        if role.startswith("@m"):
            if role in db[KEYS.ROLE]:
                role_obj = gld.get_role(db[KEYS.ROLE][role][KEYS.ID])
            else:
                role_obj = await get(gld, role[2:])
        else:
            role_obj = await get(gld, role)  # type: Role

        if role_obj is None:
            continue

        await mmbr.remove_roles(role_obj)

        # This should theoretically never happen, so 5 seconds of sleep isn't super important wait time
        if role not in db[KEYS.ROLE]:
            await sleep(5)      # Give 5 seconds sleep time to confirm that role_obj was updated with mmbr as a member
            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}

        db[KEYS.ROLE][role][KEYS.MMBR] -= 1

        print(f"Role {str(role_obj)}; Role.members: {role_obj.members}; "
              f"db[role][members]: {db[KEYS.ROLE][role][KEYS.MMBR]}")

        if not db[KEYS.ROLE][role][KEYS.MMBR]:  # If just removed last member, delete the Role
            await role_obj.delete()
            del db[KEYS.ROLE][role]

    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(new_roles)
