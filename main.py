from os import getenv
from cogs import *

from discord import Bot, Intents, NotFound, HTTPException, Guild
from discord.ext import tasks

from src import database
from src import battlenet
from src.db_keys import *
from src.config import db


def main():

    intents = Intents.default()
    intents.members = True

    bot = Bot(
        command_prefix="/",
        intents=intents,
        case_insensitive=True,
        auto_sync_commands=True
    )

    bot.add_cog(BattlenetHandler(bot))
    bot.add_cog(TeamInfoHandler(bot))
    bot.add_cog(GenericListener(bot))

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for bnet in db[BNET]:
            battlenet.update(bnet)

            if not battlenet.is_active(bnet):
                battlenet.remove(bnet)

        print("Update loop complete")

    @tasks.loop(minutes=1)
    async def dump_loop():

        # Print contents of db to userdata.json, only used for testing
        database.dump()
        print(f"Database dumped")

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")

        # Clear user data, only used for testing
        # database.clear_user_data()
        update_loop.start()
        dump_loop.start()

    async def get_dm(user):
        return user.dm_channel or await user.create_dm()

    async def get_user_named(disc, guild=None):
        if disc in db[MMBR]:
            try:
                user = await bot.fetch_user(db[MMBR][disc][ID])
            except NotFound:
                print(f"User {disc} <id={db[MMBR][disc][ID]}> does not exist")

                # If unable to find user for whatever reason, remove all of their battlenets
                db[BNET] = [k for k in db[BNET] if k not in set(db[MMBR][disc][BNET])]
                del db[MMBR][disc]  # If not real user no roles to remove anyway so just delete
            except HTTPException:
                print(f"HTTPException raised while retrieving {disc}")
                return None
            else:
                return user
        elif isinstance(guild, Guild):
            return guild.get_member_named(disc)
        else:
            for guild in bot.guilds:  # type: Guild
                user = guild.get_member_named(disc)
                if user is not None:
                    return user
            return None

    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
