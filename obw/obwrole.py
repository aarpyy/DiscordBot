from replit import db, Database
db: Database

from discord import Guild, Member, Role, Forbidden, HTTPException, Colour
from collections import deque
from sys import stderr
from datetime import timedelta

from .config import *
from .tools import loudprint
from .battlenet import is_active, is_hidden
from .request import get_role_obj, force_role_obj
from .db_keys import *

from typing import Set, Union

categ_short = {"Win Percentage": "W"}
categ_major = ("Win Percentage", "Time Played")

mention_tag = "@m"
no_tag = "--"

obw_color = Colour.from_rgb(143, 33, 23)


def time(stat: str) -> str:
    t = stat.split(":")
    if len(t) == 1:
        return t[0] + "s"
    elif len(t) == 2:
        return t[0] + "m"
    else:
        h, m, s = t
        delta = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
        if delta.days:
            return str(delta.days) + "d"
        else:
            return str(delta.seconds // 3600) + "h"

def format_stat(ctg: str, stat: str) -> str:
    if ctg == "Time Played":
        return time(stat)
    elif ctg == "Win Percentage":
        return stat + "%"
    else:
        return stat


def format_role(role: Role) -> str:
    """Returns string name of role as it appears in database

    :param role: discord role
    :type role: Role
    :return: name of role
    :rtype: str
    """
    if role.mentionable:
        return mention_tag + str(role)
    else:
        return no_tag + str(role)


async def delete_role(role: Role, rname: str = "") -> None:
    if not rname:
        rname = format_role(role)

    remove_role(rname)
    await role.delete()


def remove_role(role: str) -> None:
    """
    Removes all instances of a role from discord user by searching through all linked battlenets.

    :param disc: username
    :param role: role to be removed
    :return: None
    """

    for bnet in db[BNET]:

        # Save remove that doesn't throw error if role not in list
        db[BNET][bnet][ROLE] = list(r for r in db[BNET][bnet][ROLE] if r != role)
    
    del db[ROLE][role]


def rename_role(before: str, after: str) -> None:
    """
    Renames all instances of role by searching through all linked battlenets of all users.

    :param before: role to be renamed
    :param after: new role name
    :return: None
    """

    for bnet in db[BNET]:
        db[BNET][bnet][ROLE] = list(after if role == before else role for role in db[BNET][bnet][ROLE])


def generate_roles(bnet: str) -> Set[str]:
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles

    # Table of battlenet's statistics; STAT will always exist, but could be empty dict
    table = db[BNET][bnet][STAT].get("quickplay", {})

    # For each stat associated with battlenet, add that stat if it is an important one
    for ctg in table:
        if ctg in categ_major:
            hero = max(table[ctg], key=lambda x: table[ctg][x])
            roles.add(f"{no_tag}{hero}-{format_stat(ctg, table[ctg][hero])}" + categ_short.get(ctg, ""))

    table = db[BNET][bnet][RANK]  # Table of battlenet's competitive ranks
    rank = max(table, key=lambda x: table[x])
    roles.add(f"{no_tag}{rank.capitalize()}-{table[rank]}")

    if is_active(bnet):
        roles.add(mention_tag + bnet)
        roles.add(mention_tag + db[BNET][bnet][PTFM])
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

    loudprint(f"Updating roles for [{bnet}]...")

    if is_hidden(bnet):
        loudprint(f"[{bnet}] is hidden. No roles given")
        return

    user_id = db[MMBR][disc][ID]

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        member = await guild.fetch_member(user_id)  # type: Member
    except Forbidden as root:
        raise AttributeError(f"Unable to access Guild {str(guild)}") from root
    except HTTPException as root:
        raise ValueError(f"Fetching user {disc} <id={user_id}> failed") from root

    loudprint(f"Member fetched: {str(member)} ({member.id})")  # type: ignore

    db_roles = set(db[MMBR][disc][BNET][bnet][ROLE])
    new_roles = generate_roles(disc, bnet)

    # 'Refresh' role counts, by just subtracting member count for all current db roles
    for role in db_roles:

        # Don't worry about this reaching 0 here, we check later if its 0 and delete
        db[ROLE][role][MMBR] -= 1

    # And then adding 1 for all roles they will have after
    for role in new_roles:
        if role in db[ROLE]:
            db[ROLE][role][MMBR] += 1
        else:
            db[ROLE][role][MMBR] = 1


    # Remove role tag before sending into function so that it gets actual role name
    to_add, to_remove = get_current_roles(set(r[2:] for r in db_roles), set(r[2:] for r in new_roles), set(format_role(role) for role in member.roles))

    role: str
    for role in to_add:
        kwargs = dict(
            name=role[2:],
            color=obw_color,
            mentionable=role.startswith(mention_tag)
        )
        role_obj = await force_role_obj(guild, role, **kwargs)
        await member.add_roles(role_obj)

    for role in to_remove:
        role_obj = await get_role_obj(guild, role)  # type: ignore
        if role_obj is not None:
            await member.remove_roles(role_obj)
            if not db[ROLE][role][MMBR]:  # If just removed last member, delete the Role
                print(f"Deleting {str(role_obj)}; Role.members: {[str(m) for m in role_obj.members]}; "
                      f"db: {db[ROLE][role][MMBR]}")
                await delete_role(role_obj, role)

    db[BNET][bnet][ROLE] = list(new_roles)


def get_current_roles(db_roles: set[str], new_roles: set[str], disc_roles: set[str]):
    """Given a set of roles currently given to user from stats, a set of roles
    newly given to user from stats, and a set of roles actually held by user in 
    discord guild, return the list of roles to be added to user in guild
    and a list of roles to be remove from user in guild

    :param db_roles: current roles in database
    :type db_roles: set[str]
    :param new_roles: roles generated from new stats
    :type new_roles: set[str]
    :param disc_roles: roles held by user in guild
    :type disc_roles: set[str]
    :return: roles user should add in server, should remove in server
    :rtype: tuple[set[str]]
    """

    db_removed = db_roles - new_roles                   # Roles removed from database
    disc_remove = db_removed.intersection(disc_roles)   # Roles removed from database that were also discord roles
    disc_add = new_roles - disc_roles                   # Roles currently in database that are not discord roles

    return disc_add, disc_remove


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
    except HTTPException as exc:
        loudprint(f"Failed {update_bnet_roles.__name__}(): {str(exc)}", file=stderr)
