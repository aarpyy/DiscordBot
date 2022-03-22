# File for handling general API requests

from replit import db, Database

db: Database

from discord.ext.commands import Bot
from discord import NotFound, HTTPException, User, Member, DMChannel, Role, Guild
from discord.utils import find
from sys import stderr

from .tools import loudprint
from .db_keys import *

from typing import Union, Optional


async def dm(user: User) -> DMChannel:
    return user.dm_channel or await user.create_dm()


async def get_user(bot: Bot, disc: str, guild: Guild = None):  # type: ignore
    if disc in db[MMBR]:
        try:
            return await bot.fetch_user(db[MMBR][disc][ID])
        except NotFound:
            loudprint(f"User {disc} <id={db[MMBR][disc][ID]}> does not exist"
                      f" and has been removed from db", file=stderr)
            db[BNET] = [k for k in db[BNET] if k not in set(db[MMBR][disc][BNET])]
            del db[MMBR][disc]  # If not real user no roles to remove anyway so just delete
        except HTTPException as root:
            loudprint(f"Failed {get_user.__name__}(): {str(root)}", file=stderr)
    elif isinstance(guild, Guild):
        return guild.get_member_named(disc)
    else:
        for guild in bot.guilds:        # type: Guild
            user = guild.get_member_named(disc)
            if user is not None:
                return user
        return None


async def get_role_obj(guild: Guild, role: str) -> Optional[Role]:
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
        return guild.get_role(db[ROLE][role][ID])
    else:
        try:
            roles = await guild.fetch_roles()
        except HTTPException:
            return None
        else:
            role = role[2:]
            role_obj = find(lambda r: r.name == role, roles)
            if role_obj is not None:
                db[ROLE][role] = {ID: role_obj.id, MMBR: len(role_obj.members)}
            return role_obj


async def force_role_obj(guild: Guild, role: str, **kwargs) -> Role:
    """
    Shell function for _role_obj() that, if unable to return Role, instead creates the role.

    :param guild: guild that holds role
    :param role: rolename
    :return:
    """

    role_obj = await get_role_obj(guild, role)
    if role_obj is None:
        role_obj = await guild.create_role(**kwargs)
        db[ROLE][role] = {ID: role_obj.id, MMBR: 0}

    return role_obj
