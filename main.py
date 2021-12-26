from replit import db

from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import Intents, Member, DMChannel, Guild
from discord.message import Message

from os import getenv

import role
import database
import battlenet

from config import KEYS
from tools import jsondump


su = "aarpyy#3360"  # Creator of bot


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
        # database.refresh()
        # await database.clean_roles(bot)

        # Start loop for updated all users
        update_loop.start()

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                battlenet.update(disc, bnet)

        with open("userdata.json", "w") as outfile:
            outfile.write(jsondump(db))

        input("All user data should now be updated. Check userdata.json to confirm. ")

        # Update all roles for people in guilds
        for gld in bot.guilds:  # type: Guild
            for mmbr in gld.members:
                disc = str(mmbr)
                if disc in db[KEYS.MMBR]:
                    for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                        await role.update(gld, disc, bnet)

        with open("userdata.json", "w") as outfile:
            outfile.write(jsondump(db))

        input("All roles should now be updated. Check userdata.json and user roles to confirm. ")

        # If any accounts are marked for removal, re-run through them and remove them
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:

                # If battlenet is inactive, let user know it's removed
                if not db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE]:
                    print(f"Removing {disc}[{bnet}]...")
                    user = await bot.fetch_user(db[KEYS.MMBR][disc][KEYS.ID])
                    channel = user.dm_channel               # type: DMChannel
                    if channel is None:
                        channel = await user.create_dm()    # type: DMChannel

                    message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                              f"from your discord."

                    if prim := battlenet.remove(bnet, disc):
                        message += f"\n\nYour new primary account is {prim}"
                    await channel.send(message)

        print("Update loop complete")

    @bot.event
    async def on_message(msg: Message):
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

    async def account(ctx: Context, bnet: str, platform: str):
        """
        Attempts to link battlenet accunt to user's discord.

        :param ctx: Context of command
        :param bnet: battlenet
        :param platform: platform of battlenet
        :return: None
        """
        disc = str(ctx.author)

        if disc not in db[KEYS.MMBR]:
            db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: ctx.author.id}

        if bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            if ctx.guild is not None:
                await role.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

        with open("userdata.json", "w") as outfile:
            outfile.write(jsondump(db))

    @bot.command(name="battlenet")
    async def _battlenet(ctx: Context, bnet: str):
        await account(ctx, bnet, "PC")

    @bot.command()
    async def xbox(ctx: Context, bnet: str):
        await account(ctx, bnet, "Xbox")

    @bot.command()
    async def playstation(ctx: Context, bnet: str):
        await account(ctx, bnet, "Playstation")

    @bot.command()
    async def primary(ctx: Context, bnet: str):
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
