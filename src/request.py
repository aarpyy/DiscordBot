# File for handling general API requests

from discord.ext.commands import Bot
from discord import NotFound, HTTPException, User, DMChannel, Guild
from sys import stderr

from .db_keys import *
from .config import db


async def get_dm(user: User) -> DMChannel:
    return user.dm_channel or await user.create_dm()


async def get_user(bot: Bot, disc: str, guild: Guild = None):
    if disc in db[MMBR]:
        try:
            return await bot.fetch_user(db[MMBR][disc][ID])
        except NotFound:
            print(f"User {disc} <id={db[MMBR][disc][ID]}> does not exist"
                  f" and has been removed from db", file=stderr)

            # If unable to find user for whatever reason, remove all of their battlenets
            db[BNET] = [k for k in db[BNET] if k not in set(db[MMBR][disc][BNET])]
            del db[MMBR][disc]  # If not real user no roles to remove anyway so just delete
        except HTTPException as root:
            print(f"Failed {get_user.__name__}(): {str(root)}", file=stderr)
            return None
    elif isinstance(guild, Guild):
        return guild.get_member_named(disc)
    else:
        for guild in bot.guilds:  # type: Guild
            user = guild.get_member_named(disc)
            if user is not None:
                return user
        return None
