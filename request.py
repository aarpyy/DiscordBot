# File for handling general API requests

from replit import db

from discord.ext.commands import Bot
from discord import NotFound, HTTPException, User, Member, DMChannel, Role, Guild
from discord.utils import find
from sys import stderr

from tools import loudprint
from config import Key

from typing import Union, Optional


async def getdm(user: Union[User, Member]) -> DMChannel:
    return user.dm_channel or await user.create_dm()


async def getuser(bot: Bot, disc: str, guild: Guild = None):
    if disc in db[Key.MMBR]:
        try:
            return await bot.fetch_user(db[Key.MMBR][disc][Key.ID])
        except NotFound:
            loudprint(f"User {disc} <id={db[Key.MMBR][disc][Key.ID]}> does not exist"
                      f" and has been removed from db", file=stderr)
            db[Key.BNET] = [k for k in db[Key.BNET] if k not in set(db[Key.MMBR][disc][Key.BNET])]
            del db[Key.MMBR][disc]  # If not real user no roles to remove anyway so just delete
        except HTTPException as src:
            loudprint(f"Failed {getuser.__name__}(): {str(src)}", file=stderr)
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
    checks if the Role is already in the db, getting the Role via Role.id if true. Otherwise,
    it iterates through all Roles in Guild, attempting to match via string, returning None if no
    matches were made.

    :param guild: guild that role hopefully exists in
    :param role: name of role
    :return: Role object if it exists in the guild
    """

    if role in db[Key.ROLE]:
        return guild.get_role(db[Key.ROLE][role][Key.ID])
    else:
        try:
            roles = await guild.fetch_roles()
        except HTTPException:
            return None
        else:
            role = role[2:]
            role_obj = find(lambda r: r.name == role, roles)
            if role_obj is not None:
                db[Key.ROLE][role] = {Key.ID: role_obj.id, Key.MMBR: len(role_obj.members)}
            return role_obj


async def force_role_obj(guild: Guild, role: str, **kwargs) -> Role:
    """
    Shell function for get_role_obj() that, if unable to return Role, instead creates the role.

    :param guild: guild that holds role
    :param role: rolename
    :return:
    """

    role_obj = await get_role_obj(guild, role)
    if role_obj is None:
        role_obj = await guild.create_role(**kwargs)
        db[Key.ROLE][role] = {Key.ID: role_obj.id, Key.MMBR: 0}

    return role_obj
