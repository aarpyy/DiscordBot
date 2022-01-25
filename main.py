from replit import db

from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import (Intents, Member, DMChannel, Guild, Role, User, Forbidden, HTTPException,
                     NotFound, Reaction, Emoji, TextChannel)
from discord.message import Message

from os import getenv, system
from os.path import join, exists
from sys import exit, exc_info, stderr
from asyncio import sleep
from traceback import print_exc

import obwrole
import database
import battlenet
import reactions
import request
import messaging

from config import Key
from tools import loudprint, loudinput

from typing import Dict, Union, List

su = "aarpyy#3360"  # Creator of bot


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    # Loops

    @tasks.loop(minutes=1)
    async def dump_loop():

        # Print contents of db to userdata.json, only used for testing
        database.dump()
        loudprint("Database dumped")

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for disc in db[Key.MMBR]:
            for bnet in db[Key.MMBR][disc][Key.BNET]:
                battlenet.update(disc, bnet)

        database.dump()

        loudinput("All user data should now be updated")

        # Update all roles for people in guilds
        for guild in bot.guilds:  # type: Guild
            for mmbr in guild.members:  # type: Member
                disc = str(mmbr)
                if disc in db[Key.MMBR]:
                    for bnet in db[Key.MMBR][disc][Key.BNET]:
                        await obwrole.update(guild, disc, bnet)

        database.dump()

        loudinput("All roles should now be updated")

        # If any accounts were marked for removal, re-run through them and remove them
        for disc in db[Key.MMBR]:
            for bnet in db[Key.MMBR][disc][Key.BNET]:

                # If battlenet is inactive, let user know it's removed
                if not battlenet.is_active(disc, bnet):
                    loudprint(f"Removing {disc}[{bnet}]...")
                    user = await request.getuser(bot, disc)
                    if user is not None:
                        channel = await request.getdm(user)
                        message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                                  f"from your discord."

                        if prim := battlenet.remove(bnet, disc):
                            message += f"\n\nYour new primary account is {prim}"
                        await channel.send(message)

        loudprint("Update loop complete")

    # Events

    @bot.event
    async def on_ready():
        loudprint(f"Logged in as {bot.user}.")
        # Uncomment these for testing
        # database.refresh()
        # await database.clean_roles(bot)

        # Start loop for updated all users
        update_loop.start()
        dump_loop.start()

    @bot.event
    async def on_error(event: str, *args, **kwargs):
        print(f"event: {event}", file=stderr)
        print(f"args: {args}", file=stderr)
        print(f"kwargs: {kwargs}", file=stderr)
        print_exc(file=stderr)
        await bot.close()

    @bot.event
    async def on_reaction_add(reaction: Reaction, user: Union[User, Member]):
        message = reaction.message  # type: Message
        channel = message.channel
        guild = message.guild
        author = message.author

        # Check to confirm that reaction was in channel of guild we are interested in
        if isinstance(author, Member) and isinstance(guild, Guild) and messaging.valid_reaction(reaction) and \
                messaging.valid_channel(channel):
            emoji = reaction.emoji
            loudprint(f"Emoji: {repr(emoji)} (is custom: {reaction.custom_emoji})")
            loudprint(f"Reaction: {repr(reaction)}")
            await messaging.log_reaction(author, reaction)

        database.dump()

        loudprint("Database dumped")

    @bot.event
    async def on_member_join(member: Member):
        # If new guild member is a bot, ignore them
        if not member.bot:
            disc = str(member)
            if disc not in db[Key.MMBR]:
                db[Key.MMBR][disc] = {Key.ID: member.id, Key.RXN: {}, Key.SCORE: {}, Key.BNET: {}}

        database.dump()

    @bot.event
    async def on_guild_role_delete(role: Role):
        rname = obwrole.rolename(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[Key.ROLE]:
            obwrole.globalrm(rname)

    @bot.event
    async def on_guild_role_update(before: Role, after: Role):
        bname, aname = obwrole.rolename(before), obwrole.rolename(after)

        # If the role wasn't in db before, not a role we care about
        if bname in db[Key.ROLE]:
            del db[Key.ROLE][bname]
            await sleep(5)  # Give some sleep time for after.members to be updated
            db[Key.ROLE][aname] = {Key.ID: after.id, Key.MMBR: len(after.members)}
            obwrole.global_rename(bname, aname)

    # Commands

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

        if disc not in db[Key.MMBR]:
            db[Key.MMBR][disc] = {Key.ID: ctx.author.id, Key.RXN: {}, Key.SCORE: {}, Key.BNET: {}}

        if bnet in db[Key.MMBR][disc][Key.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[Key.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            db[Key.MMBR][disc][Key.BNET][bnet][Key.ROLE] = list(obwrole.find_battlenet_roles(disc, bnet))
            guild = ctx.guild  # type: Guild
            if guild is not None:
                await obwrole.update(guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

        database.dump()

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
    async def remove(ctx: Context, bnet: str):
        disc = str(ctx.author)
        try:
            if bnet not in db[Key.MMBR][disc][Key.BNET]:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your discord!")
        else:
            battlenet.deactivate(disc, bnet)
            guild = ctx.guild  # type: Guild
            if guild is not None:
                await obwrole.update(guild, disc, bnet)
            message = f"You have successfully unlinked {bnet} from your discord!"
            if prim := battlenet.remove(bnet, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.channel.send(message)

        database.dump()

    @bot.command()
    async def primary(ctx: Context, bnet: str):
        disc = str(ctx.author)
        try:
            user_battlenets = db[Key.MMBR][disc][Key.BNET]
            if bnet not in user_battlenets:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your account!")
        else:
            if user_battlenets[bnet][Key.PRIM]:
                await ctx.channel.send(f"{bnet} is already your primary linked account!")
            else:
                for b in user_battlenets:
                    user_battlenets[b][Key.PRIM] = False
                user_battlenets[bnet][Key.PRIM] = True
                await ctx.channel.send(f"{bnet} is your new primary linked account!")

        database.dump()

    # Log in to bot using token from replit env and run
    bot.run(getenv('TOKEN'))


if __name__ == "__main__":
    for f in ("comp", "dne", "is_private", "stats"):
        if not exists(join("get", f)):
            exit(1)

    if not exists("split"):
        system("make split")

    main()
