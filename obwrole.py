from replit import db

from discord import Guild, Member, Role, Forbidden, HTTPException, utils, Colour
from asyncio import sleep

from config import KEYS
from tools import getkey, loudprint

from typing import Optional, List, Set

categ_short = {"Win Percentage": "W"}
categ_major = ("Win Percentage", "Time Played")

mention_tag = "@m"
no_tag = "--"

obw_color = Colour.from_rgb(143, 33, 23)


# Role methods


def rolename(role: Role) -> str:
    if role.mentionable:
        return mention_tag + str(role)
    else:
        return no_tag + str(role)


async def globaldel(role: Role, rname: str = None) -> None:
    if rname is None:
        rname = rolename(role)

    globalrm(rname)
    await role.delete()


def globalrm(role: str) -> None:
    for disc in db[KEYS.MMBR]:
        remove(disc, role)
    del db[KEYS.ROLE][role]


def remove(disc: str, role: str) -> None:
    for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(
            r for r in db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] if r != role)


def rename(before: str, after: str) -> None:
    for disc in db[KEYS.MMBR]:
        for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            roles = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE]
            updated = list(after if role == before else role for role in roles)
            db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = updated


def get_bnet_roles(disc: str, bnet: str) -> Set[str]:
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles

    # Table of battlenet's statistics; KEYS.STAT will always exist, but could be empty dict
    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT].get("quickplay", {})

    # For each stat associated with battlenet, add that stat if it is an important one
    for ctg in table:
        if ctg in categ_major:
            hero = getkey(table[ctg])
            roles.add(f"{no_tag}{hero}-{table[ctg][hero]}" + categ_short.get(ctg, ""))

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK]  # Table of battlenet's competitive ranks

    for rnk in table:  # type: str
        roles.add(f"{no_tag}{rnk.capitalize()}-{table[rnk]}")

    if db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE]:
        roles.add(mention_tag + bnet)
        roles.add(mention_tag + db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PTFM])
    return roles


async def get(gld: Guild, role: str) -> Optional[Role]:
    """
    Helper function that more sufficiently ensures that the Role is returned if it exists. First, it
    checks if the Role is already in the db, getting the Role via Role.id if true. Otherwise,
    it iterates through all Roles in Guild, attempting to match via string, returning None if no
    matches were made.

    :param gld: Guild
    :param role: name of role
    :return: Optional[Role]
    """

    if role in db[KEYS.ROLE]:
        return gld.get_role(db[KEYS.ROLE][role][KEYS.ID])
    else:
        try:
            roles = await gld.fetch_roles()
        except HTTPException:
            return None
        else:
            role = role[2:]
            role_obj = utils.find(lambda rle: rle.name == role, roles)
            if role_obj is not None:
                db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}
            return role_obj


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
    loudprint(f"Updating roles for {disc}[{bnet}]...")

    user_id = db[KEYS.MMBR][disc][KEYS.ID]

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        member = await gld.fetch_member(user_id)  # type: Member
    except Forbidden as src:
        raise AttributeError(f"Unable to access Guild {str(gld)}") from src
    except HTTPException as src:
        raise ValueError(f"Fetching user {disc} <id={user_id}> failed") from src

    loudprint(f"Member fetched: {str(member)} ({member.id})")

    new_roles = get_bnet_roles(disc, bnet)  # Roles battlenet should have

    role: Role
    current_roles = set(rolename(role) for role in member.roles)  # Roles discord user currently has

    to_add = new_roles.difference(current_roles)  # Roles user should have minus roles discord thinks they have

    loudprint(f"Roles in to_add: {to_add}")

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

    # roles_held is all roles that the bot could have given the user that they DO have
    current_bot_roles = all_roles.intersection(current_roles)

    # Thus, to_remove is all the roles bot given roles minus the ones that the user SHOULD have
    to_remove = current_bot_roles.difference(new_roles)

    loudprint(f"Roles in to_remove: {to_remove}")

    # Don't increment member count for any roles in to_add, since these are not all the roles that need to be
    # incremented. Instead, take care of adding and removing of actual roles/entrance into db and later
    # increment all roles being added directly to user regardless of if the role was just created
    for role in to_add:  # type: str
        role_obj = await get(gld, role)
        if role_obj is None:
            if role.startswith(mention_tag):
                role_obj = await gld.create_role(name=role[2:], mentionable=True, color=obw_color)
            else:
                role_obj = await gld.create_role(name=role[2:], color=obw_color)

            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: 0}

        elif role not in db[KEYS.ROLE]:
            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}

        await member.add_roles(role_obj)

    for role in to_remove:  # type: str
        role_obj = await get(gld, role)  # type: Role
        if role_obj is None:
            continue

        await member.remove_roles(role_obj)

        # This should theoretically never happen, so 5 seconds of sleep isn't super important wait time
        if role not in db[KEYS.ROLE]:
            await sleep(5)  # Give 5 seconds sleep time to confirm that role_obj was updated with member
            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}
        else:
            db[KEYS.ROLE][role][KEYS.MMBR] -= 1

        if not db[KEYS.ROLE][role][KEYS.MMBR]:  # If just removed last member, delete the Role
            loudprint(f"Deleting {str(role_obj)}; Role.members: {[str(m) for m in role_obj.members]}; "
                  f"db: {db[KEYS.ROLE][role][KEYS.MMBR]}")
            await globaldel(role_obj, role)

    for role in new_roles:
        db[KEYS.ROLE][role][KEYS.MMBR] += 1

    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(new_roles)
