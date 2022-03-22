from .config import *
from replit import db, Database
from sys import exit, exc_info, stderr
if db is None:
    print(f"Database failed to load", file=stderr)
    exit(1)

db: Database

from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import (Intents, Member, DMChannel, Guild, Role, User, Forbidden, HTTPException,
                     NotFound, Reaction, Emoji, TextChannel)
from discord.message import Message
from traceback import print_exc
from functools import wraps
import asyncio

from . import obwrole
from . import database
from . import battlenet
from . import request
from . import messaging

from .db_keys import *
from .tools import loudprint, loudinput
from .compositions import Map, Round, get_map

from typing import Union

su = "aarpyy#3360"  # Creator of bot


def restrict(users=None):
    """Given a list of users, returns a wrapper that restricts
    the use of a discord command except for the given users.

    :param users: List of users with permission to use function, defaults to super user (aarpyy)
    :type users: list[str], optional
    :return: wrapper, restricting bot.command()
    :rtype: function
    """
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
                await ctx.channel.send(f"This command is currently disabled!")  # type: ignore

        return restricted

    return decorator


def main():

    # Normal intents, including managing members
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    # Loops

    @tasks.loop(minutes=1)
    async def dump_loop():

        # Print contents of db to userdata.json, only used for testing
        database.dump()

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for bnet in db[BNET]:
            battlenet.update(bnet)

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
                if not battlenet.is_active(bnet):
                    loudprint(f"Removing {disc}[{bnet}]...")
                    user = await request.get_user(bot, disc)  # type: ignore
                    if user is not None:
                        channel = await request.get_dm(user)  # type: ignore
                        message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                                  f"from your discord."

                        if prim := battlenet.remove(bnet, disc):
                            message += f"\n\nYour new primary account is {prim}"
                        await channel.send(message)

        loudprint("Update loop complete")

    # Events

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")

        # Clear user data, only used for testing
        database.clear_user_data()

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
    async def on_member_join(member: User):
        # If new guild member is a bot, ignore them
        if not member.bot:
            disc = str(member)
            if disc not in db[MMBR]:
                db[MMBR][disc] = {ID: member.id, RXN: {}, SCORE: {}, BNET: {}}

        database.dump()

    @bot.event
    async def on_guild_role_delete(role: Role):
        rname = obwrole.format_role(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[ROLE]:
            obwrole.remove_role(rname)

    @bot.event
    async def on_guild_role_update(before: Role, after: Role):
        bname, aname = obwrole.format_role(before), obwrole.format_role(after)

        # TODO: This might not need to be done like this, since role update might not mean user count changes!

        # If the role wasn't in db before, not a role we care about
        if bname in db[ROLE]:
            del db[ROLE][bname]
            await asyncio.sleep(5)      # Give some sleep time for after.members to be updated
            db[ROLE][aname] = {ID: after.id, MMBR: len(after.members)}
            obwrole.rename_role(bname, aname)

    # Commands

    @bot.command()
    async def comp(ctx: Context, *args):
        if not args:
            await ctx.channel.send("Must provide a map!")  # type: ignore
            return
        else:
            M, R = get_map(args)
            if M == Map.NoMap:
                await ctx.channel.send(f"{args[0]} is not a recognizable map!")  # type: ignore
                return

            str_emoji = {emoji.name: str(emoji) for emoji in ctx.guild.emojis}  # type: ignore
            if R != Round.All:
                heroes = db[MAP][M.value][R.value]
                composition = [str_emoji.get(e, '') for e in heroes]
                await ctx.channel.send(", ".join(composition))  # type: ignore
            else:
                message = ""
                for r in db[MAP][M.value]:           # type: str

                    #  current team composition and its readable string (with emojis)
                    heroes = db[MAP][M.value][r]
                    composition = [str_emoji.get(e, '') for e in heroes]

                    # Convert round name into nicer string
                    round_name = " ".join(s.capitalize() for s in r.split('-'))

                    # Append to message
                    message += f"{round_name}:  " + " ".join(composition) + "\n"
                await ctx.channel.send(message)  # type: ignore

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
        guild = str(ctx.guild)

        if not isinstance(ctx.guild, Guild):
            await ctx.channel.send("This command must be run on a server channel!")  # type: ignore
            return

        # If user not in database, add them
        elif disc not in db[GLD][guild][MMBR]:
            db[MMBR][disc] = {ID: ctx.author.id, RXN: {}, SCORE: {}, BNET: []}  # type: ignore

        if bnet in db[GLD][guild][MMBR][disc][BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")  # type: ignore
        elif bnet in db[BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")  # type: ignore
        else:
            battlenet.add(guild, disc, bnet, platform)
            db[BNET][bnet][ROLE] = list(obwrole.generate_roles(bnet))
            await obwrole.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")  # type: ignore

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
            await ctx.channel.send(f"{bnet} is not linked to your discord!")  # type: ignore
        else:
            battlenet.deactivate(bnet)
            guild = ctx.guild  # type: ignore
            if guild is not None:
                await obwrole.update(guild, disc, bnet)
            message = f"You have successfully unlinked {bnet} from your discord!"
            if prim := battlenet.remove(bnet, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.channel.send(message)  # type: ignore

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
            await ctx.channel.send(f"{bnet} is not linked to your account!")  # type: ignore
        else:
            if user_battlenets[bnet][PRIM]:
                await ctx.channel.send(f"{bnet} is already your primary linked account!")  # type: ignore
            else:
                for b in user_battlenets:
                    user_battlenets[b][PRIM] = False
                user_battlenets[bnet][PRIM] = True
                await ctx.channel.send(f"{bnet} is your new primary linked account!")  # type: ignore

        database.dump()

    # Log in to bot using token from replit env and run
    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
