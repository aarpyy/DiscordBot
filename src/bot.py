from discord.ext import commands, tasks
from discord import Intents, Member, Role, Guild

from sys import stderr
import asyncio

from . import database
from . import obwrole
from . import battlenet
from . import request
from .db_keys import *
from .config import db


@tasks.loop(minutes=1)
async def dump_loop():

    # Print contents of db to userdata.json, only used for testing
    database.dump()


class Oberbot(commands.Bot):

    def __init__(
            self,
            command_prefix='/',
            intents=None,
            case_insensitive=True,
            **options
    ):
        if intents is None:
            intents = Intents.default()
            intents.members = True
        bot_kwargs = {
            "command_prefix": command_prefix,
            "intents": intents,
            "case_insensitive": case_insensitive
        }

        super().__init__(**bot_kwargs, **options)

    @tasks.loop(hours=1)
    async def update_loop(self):

        # Update stats for all battlenets
        for bnet in db[BNET]:
            battlenet.update(bnet)

        # Update all roles for people in guilds
        # for guild in self.guilds:  # type: Guild
        #     for mmbr in guild.members:  # type: Member
        #         disc = str(mmbr)
        #         if disc in db[MMBR]:
        #             for bnet in db[MMBR][disc][BNET]:
        #                 await obwrole.update(guild, disc, bnet)

        # If any accounts were marked for removal, re-run through them and remove them
        for disc in db[MMBR]:
            for bnet in db[MMBR][disc][BNET]:

                # If battlenet is inactive, let user know it's removed
                if not battlenet.is_active(bnet):
                    print(f"Removing {disc}[{bnet}]...")
                    user = await request.get_user(self, disc)
                    if user is not None:
                        channel = await request.get_dm(user)
                        message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                                  f"from your discord."

                        if prim := battlenet.remove(bnet, disc):
                            message += f"\n\nYour new primary account is {prim}"
                        await channel.send(message)

        print("Update loop complete")

    async def on_ready(self):
        print(f"Logged in as {self.user}.")

        # Clear user data, only used for testing
        # database.clear_user_data()
        self.update_loop.start()
        dump_loop.start()

    async def on_error(self, event: str, *args, **kwargs):
        from sys import exc_info
        print(f"event: {event}", file=stderr)
        print(f"args: {args}", file=stderr)
        print(f"kwargs: {kwargs}", file=stderr)
        print(exc_info())

    @staticmethod
    async def on_member_join(member: Member):
        pass

    @staticmethod
    async def on_guild_role_delete(role: Role):
        rname = obwrole.format_role(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[ROLE]:
            obwrole.remove_role(rname)

    @staticmethod
    async def on_guild_role_update(before: Role, after: Role):
        bname, aname = obwrole.format_role(before), obwrole.format_role(after)

        # TODO: This might not need to be done like this, since role update might not mean user count changes!

        # If the role wasn't in db before, not a role we care about
        if bname in db[ROLE]:
            del db[ROLE][bname]
            await asyncio.sleep(5)  # Give some sleep time for after.members to be updated
            db[ROLE][aname] = {ID: after.id, MMBR: len(after.members)}
            obwrole.rename_role(bname, aname)
