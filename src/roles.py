from src.config import db

from discord import Member, Role, Forbidden, HTTPException, Colour
from discord.utils import find
from sys import stderr

from .battlenet import is_active, is_hidden
from .db_keys import *

categ_short = {"Win Percentage": "W"}
categ_major = ("Win Percentage", "Time Played")

mention_tag = "@m"
no_tag = "--"
tags = (mention_tag, no_tag)

obw_color = Colour.from_rgb(143, 33, 23)


# Functions for formatting data

def format_time(stat):
    suffix = {3: "h", 2: "m", 1: "s"}
    t = stat.split(":")
    if len(t) > 1:
        a = int(t[0])
        if int(t[1]) >= 30:
            a += 1
        return str(a) + suffix[len(t)]
    elif t[0]:
        return t[0] + "s"
    else:
        return ""


def format_stat(ctg, stat):
    if ctg == "Time Played":
        return format_time(stat)
    elif ctg == "Win Percentage":
        return stat + "%"
    else:
        return stat


def format_role(role):
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


def escape_format(role):
    """Returns string name of role as it appears in discord

    :param role: role name
    :type role: str
    :return: role name without database tags
    :rtype: str
    """
    return role[2:]


# Functions for dealing with Role objects

async def get_role_obj(guild, role):
    """
    Helper function that more sufficiently ensures that the Role is returned if it exists. First, it
    checks if the Role is already in the db, ting the Role via Role.id if true. Otherwise,
    it iterates through all Roles in Guild, attempting to match via string, returning None if no
    matches were made.

    :param guild: guild that role hopefully exists in
    :param role: name of role
    :return: Role object if it exists in the guild
    """

    if role in db[ROLE]:

        # We just have access to role id, to just return directly
        return guild.get_role(db[ROLE][role][ID])
    else:
        try:
            roles = await guild.fetch_roles()
        except HTTPException:
            return None
        else:
            role = escape_format(role)     # Get role name as it would appear in discord
            role_obj = find(lambda r: r.name == role, roles)
            if role_obj is not None:
                db[ROLE][role] = {ID: role_obj.id, MMBR: len(role_obj.members)}
            return role_obj


async def force_role_obj(guild, role, **kwargs):
    """
    Shell function for get_role_obj() that, if unable to return Role, instead creates the role.

    :param guild: guild that holds role
    :param role: rolename
    :return:
    """

    role_obj = await get_role_obj(guild, role)

    if not isinstance(role_obj, Role):
        role_obj = await guild.create_role(**kwargs)
        db[ROLE][role] = {ID: role_obj.id, MMBR: 0}

    return role_obj


async def delete_role(role, name=""):
    if not name:
        name = format_role(role)

    remove_role(name)
    await role.delete()


def remove_role(role):
    """
    Removes all instances of a role from discord user by searching through all linked battlenets.

    :param role: role to be removed
    :return: None
    """

    for bnet in db[BNET]:

        # Save remove that doesn't throw error if role not in list
        db[BNET][bnet][ROLE] = list(r for r in db[BNET][bnet][ROLE] if r != role)
    
    del db[ROLE][role]


def rename_role(before, after):
    """
    Renames all instances of role by searching through all linked battlenets of all users.

    :param before: role to be renamed
    :param after: new role name
    :return: None
    """

    for bnet in db[BNET]:   # type: str
        db[BNET][bnet][ROLE] = list(after if role == before else role for role in db[BNET][bnet][ROLE])


def adjust_roles(db_roles, new_roles, disc_roles):
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
    disc_remove = db_removed & disc_roles               # Roles removed from database that were also discord roles
    disc_add = new_roles - disc_roles                   # Roles currently in database that are not discord roles

    return disc_add, disc_remove


def generate_roles(bnet):
    """
    Gets all roles associated with given battlenet based on stats.

    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles

    # Table of battlenet's statistics; STAT will always exist, but could be empty dict
    table = db[BNET][bnet][STAT].get("quickplay", {})

    # For each stat associated with battlenet, add that stat if it is an important one
    for ctg in table:   # type: str
        if ctg in categ_major:
            hero = max(table[ctg], key=lambda x: table[ctg][x])
            roles.add(no_tag + hero + "-" + format_stat(ctg, table[ctg][hero]) + categ_short.get(ctg, ""))

    table = db[BNET][bnet][RANK]  # Table of battlenet's competitive ranks
    if table:
        rank = max(table, key=lambda x: table[x])   # type: str
        roles.add(no_tag + rank.capitalize() + "-" + table[rank])

    if is_active(bnet):
        roles.add(mention_tag + bnet)
        roles.add(mention_tag + db[BNET][bnet][PTFM])
    return roles


async def update_user_roles(guild, disc, bnet):
    """
    Gives Guild Member Role objects based off of the stats retrieved from connected battlenet.

    :param guild: Guild that the discord user belongs to
    :param disc: Discord username
    :param bnet: Linked battlenet
    :raises AttributeError: If Bot lacks access to Guild
    :raises ValueError: If Discord API unable to fetch Member
    :return: None
    """

    # We need to not give discord roles to hidden people, but still keep track in db maybe?
    # What happens if hidden user removes their account, this method is called to remove all roles
    # so they shouldn't have any so maybe this is safe?

    # if is_hidden(bnet):
    #     print(f"[{bnet}] is hidden. No roles given")
    #     return

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        member: Member = await guild.fetch_member(db[MMBR][disc][ID])
    except Forbidden:
        print(f"Unable to access Guild {str(guild)}")
    except HTTPException:
        print(f"Fetching user {disc} <id={db[MMBR][disc][ID]}> failed")
    except ValueError:
        print(f"No member {disc} with id={db[MMBR][disc][ID]} in {str(guild)}")
    else:

        def rm_role(r):
            role_obj = await get_role_obj(guild, r)

            if role_obj is not None:
                await member.remove_roles(role_obj)

                if db[ROLE][role][MMBR] == 0:  # If just removed last member, delete the Role
                    print(f"Deleting {str(role_obj)}")
                    await delete_role(role_obj, role)

        def add_role(r):
            kwargs = dict(
                name=escape_format(r),
                color=obw_color,
                mentionable=r.startswith(mention_tag)
            )
            role_obj = await force_role_obj(guild, role, **kwargs)
            await member.add_roles(role_obj)

        # Current roles member has in discord server
        discord_roles = set(format_role(r) for r in member.roles)

        # Roles that the user should have based on battlenet stats
        new_roles = generate_roles(bnet)

        if not is_active(bnet):
            db_roles = []  # All roles given to user by all battlenets, including duplicates
            for b in db[MMBR][disc][BNET]:
                db_roles.extend(r for r in db[BNET][b][ROLE])

            bnet_roles = set(db[BNET][bnet][ROLE])  # Roles given to user by inactive battlenet
            for role in bnet_roles:
                db_roles.remove(role)

            # We want to remove all of the roles UNIQUELY given to user by this battlenet
            # so we remove all of roles given by battlenet from list of all roles, then
            # any roles that are given by battlenet and still not found in total roles
            # were UNIQUE to this battlenet and therefore should be removed
            to_remove = set(r for r in bnet_roles if r not in db_roles)
            db[BNET][bnet][ROLE] = []
            for role in to_remove:
                db[ROLE][role][MMBR] -= 1

                # Uncomment this to start working with actual roles
                # if role in discord_roles:
                #     rm_role(role)

            return

        # Get all roles user has in database, regardless of which battlenet it's coming from
        db_roles = set()
        for b in db[MMBR][disc][BNET]:
            for r in db[BNET][b][ROLE]:
                db_roles.add(r)

        # Remove role tag before sending into function so that it gets actual role name
        to_add, to_remove = adjust_roles(db_roles, new_roles, discord_roles)

        print(f"Adding roles: {to_add}\nRemoving roles: {to_remove}")

        db[BNET][bnet][ROLE] = list(new_roles)

        role: str
        for role in to_add:

            if role in db[ROLE]:
                db[ROLE][role][MMBR] += 1
            else:
                db[ROLE][role] = {
                    MMBR: 1,
                    ID: len(db[ROLE][role])     # Replace with actual role id
                }

            # For now, don't actually add roles in discord
            # if not is_hidden(bnet):
            #     add_role(role)

        for role in to_remove:

            # Don't worry about this reaching 0 here, we check later if its 0 and delete
            db[ROLE][role][MMBR] -= 1

            # Same as above, don't deal with discord roles yet
            # if not is_hidden(bnet):
            #     rm_role(role)
