from discord.ext import commands
from src import roles
from src.db_keys import *
from src.config import db
import asyncio


class GenericListener(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event: str, *args, **kwargs):
        from sys import exc_info, stderr
        print(f"event: {event}", file=stderr)
        print(f"args: {args}", file=stderr)
        print(f"kwargs: {kwargs}", file=stderr)
        print(exc_info())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        rname = roles.format_role(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[ROLE]:
            roles.remove_role(rname)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        bname, aname = roles.format_role(before), roles.format_role(after)

        # TODO: This might not need to be done like this, since role update might not mean user count changes!

        # If the role wasn't in db before, not a role we care about
        if bname in db[ROLE]:
            del db[ROLE][bname]
            await asyncio.sleep(5)  # Give some sleep time for after.members to be updated
            db[ROLE][aname] = {ID: after.id, MMBR: len(after.members)}
            roles.rename_role(bname, aname)
