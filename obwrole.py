from replit import db

from discord import Guild, Member, Role, Forbidden, HTTPException, Colour
from collections import deque
from sys import stderr

from config import Key
from tools import loudprint
from battlenet import is_active, is_hidden
from request import get_role_obj, force_role_obj

from typing import Set, Union

categ_short = {"Win Percentage": "W"}
categ_major = ("Win Percentage", "Time Played")

mention_tag = "@m"
no_tag = "--"

obw_color = Colour.from_rgb(143, 33, 23)


def gettime(stat: int) -> str:
    hms = deque()
    for _ in range(3):
        stat, value = divmod(stat, 60)
        hms.appendleft(value)

    for v, u in zip(hms, ("h", "m", "s")):
        if v:
            return str(v) + u
    return "0s"


def getstat(ctg: str, stat: Union[int, float, str]) -> str:
    if isinstance(stat, float):
        return str(stat)
    elif isinstance(stat, str):
        return stat
    elif ctg == "Time Played":
        return gettime(stat)
    elif "Accuracy" in ctg or "Percentage" in ctg:
        return str(stat) + '%'
    else:
        return str(stat)


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
    for disc in db[Key.MMBR]:
        remove_user_role(disc, role)
    del db[Key.ROLE][role]


def remove_user_role(disc: str, role: str) -> None:
    """
    Removes all instances of a role from discord user by searching through all linked battlenets.

    :param disc: username
    :param role: role to be removed
    :return: None
    """

    for bnet in db[Key.MMBR][disc][Key.BNET]:
        db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE] = list(
            r for r in db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE] if r != role)


def global_rename(before: str, after: str) -> None:
    """
    Renames all instances of role by searching through all linked battlenets of all users.

    :param before: role to be renamed
    :param after: new role name
    :return: None
    """

    for disc in db[Key.MMBR]:
        for bnet in db[Key.MMBR][disc][Key.BNET]:
            roles = db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE]
            updated = list(after if role == before else role for role in roles)
            db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE] = updated


async def give_role(guild: Guild, member: Member, role: Union[str, Role]) -> None:
    if isinstance(role, Role):
        role_obj = role
    else:
        role_obj = await get_role_obj(guild, role)
        if role_obj is None:
            role_obj = await guild.create_role(name=role[2:], mentionable=role.startswith(mention_tag), color=obw_color)
            db[Key.ROLE][role] = {Key.ID: role_obj.id, Key.MMBR: 1}
    await member.add_roles(role_obj)


async def donate_role(guild: Guild, former: Member, new: Member, role: Union[str, Role]) -> None:
    if isinstance(role, Role):
        role_obj = role
    else:
        role_obj = await get_role_obj(guild, role)
        if role_obj is None:
            role_obj = await guild.create_role(name=role[2:], mentionable=role.startswith(mention_tag), color=obw_color)
            db[Key.ROLE][role] = {Key.ID: role_obj.id, Key.MMBR: 1}
    if role_obj in former.roles:
        await former.remove_roles(role_obj)
    await new.add_roles(role_obj)


def find_battlenet_roles(disc: str, bnet: str) -> Set[str]:
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles

    # Table of battlenet's statistics; Key.STAT will always exist, but could be empty dict
    table = db[Key.MMBR][disc][Key.BNET][bnet][Key.STAT].get("quickplay", {})

    # For each stat associated with battlenet, add that stat if it is an important one
    for ctg in table:
        if ctg in categ_major:
            hero = max(table[ctg], key=lambda x: table[ctg][x])
            roles.add(f"{no_tag}{hero}-{getstat(ctg, table[ctg][hero])}" + categ_short.get(ctg, ""))

    table = db[Key.MMBR][disc][Key.BNET][bnet][Key.RANK]  # Table of battlenet's competitive ranks
    rank = max(table, key=lambda x: table[x])
    roles.add(f"{no_tag}{rank.capitalize()}-{table[rank]}")

    if is_active(disc, bnet):
        roles.add(mention_tag + bnet)
        roles.add(mention_tag + db[Key.MMBR][disc][Key.BNET][bnet][Key.PTFM])
    return roles


async def update_bnet_roles(guild: Guild, disc: str, bnet: str) -> None:
    """
    Gives Guild Member Role objects based off of the stats retrieved from connected battlenet.

    :param guild: Guild that the discord user belongs to
    :param disc: Discord username
    :param bnet: Linked battlenet
    :raises AttributeError: If Bot lacks access to Guild
    :raises ValueError: If Discord API unable to fetch Member
    :return: None
    """

    loudprint(f"Updating roles for {disc}[{bnet}]...")

    if is_hidden(disc, bnet):
        loudprint(f"{disc}[{bnet}] is hidden. No roles given")
        return

    user_id = db[Key.MMBR][disc][Key.ID]

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        member = await guild.fetch_member(user_id)  # type: Member
    except Forbidden as src:
        raise AttributeError(f"Unable to access Guild {str(guild)}") from src
    except HTTPException as src:
        raise ValueError(f"Fetching user {disc} <id={user_id}> failed") from src

    loudprint(f"Member fetched: {str(member)} ({member.id})")

    # To calculate roles to add, first get all roles that this battlenet should have, then subtract the roles
    # from that set that the user already has

    role: Role
    current_discord_roles = set(rolename(role) for role in member.roles)
    new_bnet_roles = find_battlenet_roles(disc, bnet)
    current_bnet_roles = set(db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE])
    to_add = new_bnet_roles - current_discord_roles

    loudprint(f"Roles in to_add: {to_add}")

    # To calculate roles to remove, get all roles that the user currently has minus the roles that they are
    # going to have after the update. The intersection of this set with all roles that the discord user
    # actually has returns the roles that the user has in discord that should be removed. This set
    # now needs to be cross referenced with all the other linked battlenets for this discord user, since
    # if two battlenets give the user the same role, if one battlenet removes the role the user should
    # still keep the role.

    to_remove = (current_bnet_roles - new_bnet_roles) & current_discord_roles
    for b in db[Key.MMBR][disc][Key.BNET]:
        if b != bnet:
            to_remove -= set(db[Key.MMBR][disc][Key.BNET][b][Key.ROLE])

    roles_lost = current_bnet_roles - new_bnet_roles

    loudprint(f"Roles in to_remove: {to_remove}")

    # Don't increment member count for any roles in to_add, since these are not all the roles that need to be
    # incremented. Instead, take care of adding and removing of actual roles/entrance into db and later
    # increment all roles being added directly to user regardless of if the role was just created
    for role in to_add:  # type: str
        kwargs = dict(
            name=role[2:],
            color=obw_color,
            mentionable=role.startswith(mention_tag)
        )
        role_obj = await force_role_obj(guild, role, **kwargs)

        if role not in db[Key.ROLE]:
            db[Key.ROLE][role] = {Key.ID: role_obj.id, Key.MMBR: len(role_obj.members)}

        await member.add_roles(role_obj)

    for role in new_bnet_roles:
        db[Key.ROLE][role][Key.MMBR] += 1

    for role in roles_lost:
        db[Key.ROLE][role][Key.MMBR] -= 1

    for role in to_remove:  # type: str
        role_obj = await get_role_obj(guild, role)  # type: Role
        if role_obj is None:
            continue

        await member.remove_roles(role_obj)

        if not db[Key.ROLE][role][Key.MMBR]:  # If just removed last member, delete the Role
            loudprint(f"Deleting {str(role_obj)}; Role.members: {[str(m) for m in role_obj.members]}; "
                      f"db: {db[Key.ROLE][role][Key.MMBR]}")
            await globaldel(role_obj, role)

    db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE] = list(new_bnet_roles)


async def update(guild: Guild, disc: str, bnet: str):
    """
    Shell function for main update_bnet_roles() function that handles possible errors.

    :param guild: Guild object user is a part of
    :param disc: username
    :param bnet: battlenet to be updated
    :return: None
    """
    try:
        await update_bnet_roles(guild, disc, bnet)
    except Forbidden:
        await guild.leave()
        loudprint(f"Left {str(guild)} guild because inaccessible", file=stderr)
    except HTTPException as src:
        loudprint(f"Failed {update_bnet_roles.__name__}(): {str(src)}", file=stderr)
