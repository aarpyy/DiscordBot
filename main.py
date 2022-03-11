from replit import db

from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import (Intents, Member, DMChannel, Guild, Role, User, Forbidden, HTTPException,
                     NotFound, Reaction, Emoji, TextChannel)
from discord.message import Message

from os import getenv, system, chdir
from pathlib import Path
from sys import exit, exc_info, stderr
from asyncio import sleep
from traceback import print_exc
from functools import wraps

import obwrole
import database
import battlenet
import reactions
import request
import messaging

from session import Session

from config import *
from tools import loudprint, loudinput

from typing import Dict, Union, List

su = "aarpyy#3360"  # Creator of bot


def restrict(users=None):
    if users is None:
        global su
        users = [su]

    def decorator(f):

        global su

        @wraps(f)
        async def restricted(ctx: Context, *args):
            if str(ctx.author) in users:
                return await f(ctx, *args)
            else:
                print(f"{str(ctx.author)} ran {f.__name__} and was blocked.", file=stderr)
                await ctx.channel.send(f"This command is currently disabled!")

        return restricted

    return decorator


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
        return

        # Update stats for all battlenets
        for disc in db[MMBR]:
            for bnet in db[MMBR][disc][BNET]:
                battlenet.update(disc, bnet)

        database.dump()

        loudinput("All user data should now be updated")

        # Update all roles for people in guilds
        for guild in bot.guilds:  # type: Guild
            for mmbr in guild.members:  # type: Member
                disc = str(mmbr)
                if disc in db[MMBR]:
                    for bnet in db[MMBR][disc][BNET]:
                        await obwrole.update(guild, disc, bnet)

        database.dump()

        loudinput("All roles should now be updated")

        # If any accounts were marked for removal, re-run through them and remove them
        for disc in db[MMBR]:
            for bnet in db[MMBR][disc][BNET]:

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
            if disc not in db[MMBR]:
                db[MMBR][disc] = {ID: member.id, RXN: {}, SCORE: {}, BNET: {}}

        database.dump()

    @bot.event
    async def on_guild_role_delete(role: Role):
        rname = obwrole.rolename(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[ROLE]:
            obwrole.globalrm(rname)

    @bot.event
    async def on_guild_role_update(before: Role, after: Role):
        bname, aname = obwrole.rolename(before), obwrole.rolename(after)

        # If the role wasn't in db before, not a role we care about
        if bname in db[ROLE]:
            del db[ROLE][bname]
            await sleep(5)  # Give some sleep time for after.members to be updated
            db[ROLE][aname] = {ID: after.id, MMBR: len(after.members)}
            obwrole.global_rename(bname, aname)

    # Commands

    @bot.command()
    async def comp(ctx: Context, *args):
        first = args[0].lower()
        if len(args) > 1:
            if first in ("lijiang-tower", "lijiang", "lijaing"):
                _map = "lijiang-tower"
                if len(args) == 2 and args[1].lower() == "tower":
                    second = args[2].lower()
                else:
                    second = args[1].lower()

                if second is None:
                    _round = None
                elif second in db[MAP][_map]:
                    _round = second
                elif second in ("control", "control-center", "controlcenter"):
                    _round = "control-center"
                elif second in ("night", "market", "night-market", "nightmarket"):
                    _round = "night-market"
                else:
                    _round = None
            elif first in (
                    "watchpoint-gibraltar", "watchpoint-gibralter", "watchpoint",
                    "watchpoint:", "gibraltar", "gibralter"
            ):
                _map = "watchpoint-gibraltar"
                second = args[1].lower()
                if second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                elif second in ("gibraltar", "gibralter") and len(args) > 2:
                    third = args[2].lower()
                    if third in ("offense", "off", "o"):
                        _round = "offense"
                    elif third in ("defense", "def", "d"):
                        _round = "defense"
                    else:
                        _round = None
                else:
                    _round = None
            elif first in ("volskaya-industries", "volskaya"):
                _map = "volskaya-industries"
                second = args[1].lower()
                if second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                elif second == "industries" and len(args) > 2:
                    third = args[2].lower()
                    if third in ("offense", "off", "o"):
                        _round = "offense"
                    elif third in ("defense", "def", "d"):
                        _round = "defense"
                    else:
                        _round = None
                else:
                    _round = None
            elif first in ("temple-of-anubis", "temple", "anubis", "aboobis"):
                _map = "temple-of-anubis"
                second = args[1].lower()
                if second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                elif len(args) > 2:
                    i = 2
                    while args[i].lower() in ("of", "anubis", "aboobis"):
                        i += 1
                        if i >= len(args):
                            _round = None
                            break
                    if second in ("offense", "off", "o"):
                        _round = "offense"
                    elif second in ("defense", "def", "d"):
                        _round = "defense"
                    else:
                        _round = None
                else:
                    _round = None
            elif first in ("blizzard-world", "blizzard", "bliz", "blizz"):
                _map = "blizzard-world"
                second = args[1].lower()
                if second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                elif second == "world" and len(args) > 2:
                    third = args[2].lower()
                    if third in ("offense", "off", "o"):
                        _round = "offense"
                    elif third in ("defense", "def", "d"):
                        _round = "defense"
                    else:
                        _round = None
                else:
                    _round = None
            elif first in ("kings-row", "kings", "king's", "kr"):
                _map = "kings-row"
                second = args[1].lower()
                if second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                elif second == "row" and len(args) > 2:
                    third = args[2].lower()
                    if third in ("offense", "off", "o"):
                        _round = "offense"
                    elif third in ("defense", "def", "d"):
                        _round = "defense"
                    else:
                        _round = None
                else:
                    _round = None
            elif first in db[MAP]:
                second = args[1].lower()
                if second in db[MAP][first]:
                    _round = second
                elif second in ("offense", "off", "o"):
                    _round = "offense"
                elif second in ("defense", "def", "d"):
                    _round = "defense"
                else:
                    _round = None
                _map = first
            else:
                await ctx.channel.send("Not a recognized map!")
                return
        elif len(args) == 0:
            await ctx.channel.send("Must provide a map!")
            return
        elif first in db[MAP]:
            _map = first
            _round = None
        else:
            _round = None
            if first in ("lijiang-tower", "lijiang", "lijaing"):
                _map = "lijiang-tower"
            elif first in (
                    "watchpoint-gibraltar", "watchpoint-gibralter", "watchpoint",
                    "watchpoint:", "gibraltar", "gibralter"
            ):
                _map = "watchpoint-gibraltar"
            elif first in ("volskaya-industries", "volskaya"):
                _map = "volskaya-industries"
            elif first in ("temple-of-anubis", "temple", "anubis", "aboobis"):
                _map = "temple-of-anubis"
            elif first in ("blizzard-world", "blizzard", "bliz", "blizz"):
                _map = "blizzard-world"
            elif first in ("kings-row", "kings", "king's", "kr"):
                _map = "kings-row"
            else:
                await ctx.channel.send("Not a recognized map!")
                return

        str_emoji = {emoji.name: str(emoji) for emoji in ctx.guild.emojis}
        if _round is not None and _round in db[MAP][_map]:
            heroes = db[MAP][_map][_round]
            composition = [str_emoji.get(e, '') for e in heroes]
            await ctx.channel.send(", ".join(composition))
        else:
            message = ""
            for rnd in db[MAP][_map]:           # type: str
                heroes = db[MAP][_map][rnd]
                composition = [str_emoji.get(e, '') for e in heroes]
                message += f"{rnd.replace('-', ' ').capitalize()}: " + ", ".join(composition) + "\n"
            await ctx.channel.send(message)

    @bot.command(name="eval")
    @restrict()
    async def _eval(ctx, *args):
        tmp = globals()
        tmp.update(locals())
        res = eval(' '.join(args), tmp)
        await ctx.channel.send(f"Eval: {res}")

    @restrict()
    async def account(ctx: Context, bnet: str, platform: str):
        """
        Attempts to link battlenet accunt to user's discord.

        :param ctx: Context of command
        :param bnet: battlenet
        :param platform: platform of battlenet
        :return: None
        """
        disc = str(ctx.author)

        if disc not in db[MMBR]:
            db[MMBR][disc] = {ID: ctx.author.id, RXN: {}, SCORE: {}, BNET: {}}

        if bnet in db[MMBR][disc][BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            db[MMBR][disc][BNET][bnet][ROLE] = list(obwrole.find_battlenet_roles(disc, bnet))
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
    @restrict()
    async def remove(ctx: Context, bnet: str):
        disc = str(ctx.author)
        try:
            if bnet not in db[MMBR][disc][BNET]:
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
    @restrict()
    async def primary(ctx: Context, bnet: str):
        disc = str(ctx.author)
        try:
            user_battlenets = db[MMBR][disc][BNET]
            if bnet not in user_battlenets:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your account!")
        else:
            if user_battlenets[bnet][PRIM]:
                await ctx.channel.send(f"{bnet} is already your primary linked account!")
            else:
                for b in user_battlenets:
                    user_battlenets[b][PRIM] = False
                user_battlenets[bnet][PRIM] = True
                await ctx.channel.send(f"{bnet} is your new primary linked account!")

        database.dump()

    @bot.command()
    @restrict()
    async def init(ctx: Context):
        database.init()

    @bot.command(name="logout")
    @restrict()
    async def _logout(ctx: Context):

        # Undoes all changes recently made on server's bot is a part of
        await test_session.clear()

    # Log in to bot using token from replit env and run
    bot.run(getenv('DISC_TOKEN'))

    test_session = Session(bot)


if __name__ == "__main__":
    root = Path(__file__).parent
    for file in ("comp", "dne", "is_private", "stats"):
        if not root.joinpath(f"GET/{file}").is_file():
            exit(1)

    if not root.joinpath("split/split"):
        chdir("split")
        system("make split")

    database.map_compositions()
    main()
