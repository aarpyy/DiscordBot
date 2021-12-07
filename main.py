from discord.ext import commands, tasks
from discord import Intents
from discord import *
from asyncio import sleep
import os
import add
import config
from config import KEYS, create_user_index
import request
import role
from replit import db
import remove

SUPERUSER = "aarpyy#3360"


def main():
    intents = Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")

        for gld in bot.guilds:
            for mmbr in gld.members:
                if str(mmbr) not in db:
                    db[str(mmbr)] = create_user_index()
                    print(f"Added {str(mmbr)} to the database")

        # Start loop for updated all users
        # update_loop.start()

    @tasks.loop(hours=1)
    async def update_loop():
        # Request for all loaded battlenets
        # request.update()

        # Iterate through guilds and update roles for everyone
        for gld in bot.guilds:
            await role.refresh(gld)
            await sleep(5)              # Give time for request to go through and user to be fully updated w/ roles
        print("Updated all accounts")

    @bot.event
    async def on_member_join(mmbr):
        # If new guild member is a bot, ignore them
        if mmbr.bot:
            db[KEYS.BOT].append(mmbr)
            return

        db[str(mmbr)] = create_user_index()
        db[KEYS.MMBR].append(str(mmbr))

    @bot.command()
    async def battlenet(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif bnet in db[disc][KEYS.ALL]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'PC')

    @bot.command()
    async def xbox(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif bnet in db[disc][KEYS.ALL]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'Xbox')

    @bot.command()
    async def playstation(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif bnet in db[disc][KEYS.ALL]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'Playstation')

    @bot.command(name="remove")
    async def _remove(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif bnet not in db:
            await ctx.channel.send(f"{bnet} not linked to any discord!")
        elif bnet not in db[disc][KEYS.ALL]:
            await ctx.channel.send(f"{bnet} is linked to another account!")
        elif bnet == db[disc][KEYS.PRIM]:
            remove.battlenet(bnet, disc)
            if len(db[disc][KEYS.ALL]) > 0:
                db[disc][KEYS.PRIM] = db[disc][KEYS.ALL][0]
                await ctx.channel.send(f"{bnet} successfully unlinked. "
                                       f"Your new primary account is {db[disc][KEYS.PRIM]}")
            else:
                db[disc][KEYS.PRIM] = None
                await ctx.channel.send(f"{bnet} successfully unlinked. You have no other linked accounts.")
        else:
            remove.battlenet(bnet)
            await ctx.channel.send(f"{bnet} successfully unlinked from your account!")

    @bot.command()
    async def primary(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif bnet in db[disc][KEYS.ALL]:
            if bnet == db[disc][KEYS.PRIM]:
                await ctx.channel.send(f"{bnet} is already your primary!")
            else:
                db[disc][KEYS.PRIM] = bnet
                await ctx.channel.send(f"{bnet} is your new primary!")
        elif bnet in db:
            await ctx.channel.send(f"{bnet} is linked to another user!")
        else:
            await ctx.channel.send(f"{bnet} is not yet linked! Try running /battlenet to link it")

    @bot.command()
    async def stats(ctx, index=None):
        disc = str(ctx.author)
        if disc not in db:
            await ctx.channel.send(f"You aren't a member of a discord server that uses this bot!")
        elif index is None:
            if db[disc][KEYS.PRIM] is None:
                await ctx.channel.send(f"You haven't linked any battlenet accounts yet!")
            else:
                bnet_data = db[db[disc][KEYS.PRIM]]
                await ctx.channel.send(f"{index}'s rank:\n{str(bnet_data[KEYS.RANK])}")
                await ctx.channel.send(f"{index}'s stats:\n{str(bnet_data[KEYS.STAT])}")
        elif index in db[KEYS.BNET]:    # If index given is a battlenet
            bnet_data = db[index]
            await ctx.channel.send(f"{index}'s rank:\n{str(bnet_data[KEYS.RANK])}")
            await ctx.channel.send(f"{index}'s stats:\n{str(bnet_data[KEYS.STAT])}")
        elif index in db:               # If index given is user's discord
            disc = index
            if db[disc][KEYS.PRIM] is None:
                await ctx.channel.send(f"{disc} doesn't have linked any battlenet accounts yet!")
            else:
                bnet_data = db[db[disc][KEYS.PRIM]]
                await ctx.channel.send(f"{index}'s rank:\n{str(bnet_data[KEYS.RANK])}")
                await ctx.channel.send(f"{index}'s stats:\n{str(bnet_data[KEYS.STAT])}")
        else:
            await ctx.channel.send(f"Couldn't find a discord or battlenet username that matches {index}")

    # Log in to bot using token from replit env and run
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    config.init()
    main()
