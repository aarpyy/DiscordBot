from discord.ext import tasks
from discord.ext.commands import Bot
from discord import Intents, Member, User, DMChannel, Guild

from os import getenv
from replit import db
from replit.database.database import ObservedList, ObservedDict

import json

import add
from config import KEYS
import role
import database
import update
import remove

from collections.abc import MutableMapping, MutableSequence

su = "aarpyy#3360"  # Creator of bot


def jsonify(o):
    if isinstance(o, str):
        return f'"{o}"'
    elif isinstance(o, bool):
        return str(o).lower()
    else:
        return str(o)


def printdb(o, indent=4):

    def _printdb(o, i):
        if isinstance(o, MutableMapping):
            s = "{"
            prefix = " " * i
            s += ",".join(f"\n{prefix}{jsonify(k)}: {_printdb(v, i + indent)}" for k, v in o.items())
            if o:
                s += "\n" + " " * (i - indent)
            return s + "}"
        elif isinstance(o, MutableSequence):
            s = "["
            prefix = " " * i
            s += ",".join(f"\n{prefix}{jsonify(e)}" for e in o)
            if o:
                s += "\n" + " " * (i - indent)
            return s + "]"
        else:
            return jsonify(o)

    return _printdb(o, indent) + "\n"


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
        database.refresh()

        # Start loop for updated all users
        update_loop.start()

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                update.user_data(disc, bnet)

        with open("userdata.json", "w") as outfile:
            outfile.write(printdb(db))

        input("All user data should now be updated. Check userdata.json to confirm. ")

        # Update all roles for people in guilds
        for gld in bot.guilds:  # type: Guild
            for mmbr in gld.members:
                disc = str(mmbr)
                if disc in db[KEYS.MMBR]:
                    for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                        await role.update(gld, disc, bnet)

        with open("userdata.json", "w") as outfile:
            outfile.write(printdb(db))

        input("All roles should now be updated. Check userdata.json and user roles to confirm. ")

        # If any accounts are marked for removal, re-run through them and remove them
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:

                # If battlenet is inactive, let user know it's removed
                if not db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE]:
                    user = await bot.fetch_user(db[KEYS.MMBR][disc][KEYS.ID])
                    channel = user.dm_channel               # type: DMChannel
                    if channel is None:
                        channel = await user.create_dm()    # type: DMChannel
                    message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                              f"from your discord."
                    if prim := remove.battlenet(bnet, disc):
                        message += f"\n\nYour new primary account is {prim}"
                    await channel.send(message)

        print("Update loop complete")

    @bot.event
    async def on_message(msg):
        if msg.author == bot.user:
            return
        elif str(msg.author) == su:
            await bot.process_commands(msg)

    @bot.event
    async def on_member_join(mmbr: Member):
        # If new guild member is a bot, ignore them
        if not mmbr.bot:
            disc = str(mmbr)
            if disc not in db[KEYS.MMBR]:
                db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: mmbr.id}

    @bot.command(name="eval")
    async def _eval(ctx, *args):
        tmp = globals()
        tmp.update(locals())
        res = eval(' '.join(args), tmp)
        await ctx.channel.send(f"Eval: {res}")

    @bot.command()
    async def battlenet(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db[KEYS.MMBR]:
            db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: ctx.author.id}
        if bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'PC')
            if ctx.guild is not None:
                await role.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

    @bot.command()
    async def xbox(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db[KEYS.MMBR]:
            db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: ctx.author.id}
        if bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'Xbox')
            if ctx.guild is not None:
                await role.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

    @bot.command()
    async def playstation(ctx, bnet):
        disc = str(ctx.author)
        if disc not in db[KEYS.MMBR]:
            db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: ctx.author.id}
        if bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            add.battlenet(disc, bnet, 'Playstation')
            if ctx.guild is not None:
                await role.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

    @bot.command()
    async def primary(ctx, bnet):
        disc = str(ctx.author)
        try:
            user_battlenets = db[KEYS.MMBR][disc][KEYS.BNET]
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your account!")
        else:
            if user_battlenets[bnet][KEYS.PRIM]:
                await ctx.channel.send(f"{bnet} is already your primary linked account!")
            else:
                for b in user_battlenets:
                    user_battlenets[b][KEYS.PRIM] = False
                user_battlenets[bnet][KEYS.PRIM] = True
                await ctx.channel.send(f"{bnet} is your new primary linked account!")

    # Log in to bot using token from replit env and run
    bot.run(getenv('TOKEN'))


if __name__ == '__main__':
    main()
