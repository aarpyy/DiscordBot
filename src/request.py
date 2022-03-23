# File for handling general API requests

from replit import db, Database

db: Database

from discord.ext.commands import Bot
from discord import NotFound, HTTPException, User, Member, DMChannel, Role, Guild
from discord.utils import find
from sys import stderr

from .tools import loudprint
from .db_keys import *

from typing import Optional


async def dm(user: User) -> DMChannel:
    return user.dm_channel or await user.create_dm()


async def get_user(bot: Bot, disc: str, guild: Guild = None):  
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
