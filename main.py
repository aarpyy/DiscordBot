from discord.ext import commands, tasks
from discord import Intents
from discord import *
from asyncio import sleep
import os
import add
import config
from config import KEYS
import request
import role
import db_commands as db_cmd
from replit import db
import retrieve
import remove
import init

SUPERUSER = "aarpyy#3360"


def main():
    intents = Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
        init.database()
        for gld in bot.guilds:
            init.members(gld)
        # Start loop for updated all users
        update_loop.start()

    @tasks.loop(hours=1)
    async def update_loop():
        # Request for all loaded battlenets
        request.update()

        # Iterate through guilds and update roles for everyone
        for gld in bot.guilds:
            await role.refresh(gld)
            await sleep(5)              # Give time for request to go through and user to be fully updated w/ roles
        print("Updated all accounts")

    @bot.command(pass_context=True)
    @bot.event
    async def on_member_join(ctx, mmbr):
        # If new guild member is a bot, ignore them
        if mmbr.bot:
            db[KEYS.BOT].append(mmbr)
            return

        gld = ctx.guild
        db[mmbr] = {KEYS.PRIM: None, KEYS.ALL: [], KEYS.ROLE: set()}
        if mmbr not in db[KEYS.MMBR]:
            db[KEYS.MMBR].append(mmbr)


    # Log in to bot using token from replit env and run
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    config.init()
    main()
