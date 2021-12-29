from replit import db

from discord.ext import tasks
from discord.ext.commands import Bot, Context
from discord import Intents, Member, DMChannel, Guild, Role, User
from discord.message import Message

from os import getenv, system
from os.path import join, exists
from sys import exit, exc_info, stderr
from asyncio import sleep

import obwrole
import database
import battlenet

from config import KEYS

from typing import Dict, Union


su = "aarpyy#3360"  # Creator of bot


async def getdm(user: Union[User, Member]) -> DMChannel:
    channel = user.dm_channel
    if channel is None:
        channel = await user.create_dm()
    return channel


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    # Loops

    @tasks.loop(seconds=30)
    async def dump_loop():

        # Print contents of db to userdata.json, only used for testing
        database.dump()

    @tasks.loop(hours=1)
    async def update_loop():

        # Update stats for all battlenets
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                battlenet.update(disc, bnet)

        database.dump()

        input("All user data should now be updated. Check userdata.json to confirm. ")

        # Update all roles for people in guilds
        for gld in bot.guilds:  # type: Guild
            for mmbr in gld.members:  # type: Member
                disc = str(mmbr)
                if disc in db[KEYS.MMBR]:
                    for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
                        await obwrole.update(gld, disc, bnet)

        database.dump()

        input("All roles should now be updated. Check userdata.json and user roles to confirm. ")

        # If any accounts are marked for removal, re-run through them and remove them
        for disc in db[KEYS.MMBR]:
            for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:

                # If battlenet is inactive, let user know it's removed
                if not db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE]:
                    print(f"Removing {disc}[{bnet}]...")
                    channel = await getdm(await bot.fetch_user(db[KEYS.MMBR][disc][KEYS.ID]))

                    message = f"Stats for {bnet} were unable to be updated and the account was unlinked " \
                              f"from your discord."

                    if prim := battlenet.remove(bnet, disc):
                        message += f"\n\nYour new primary account is {prim}"
                    await channel.send(message)

        database.dump()

        print("Update loop complete")

    # Events

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
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
        print(exc_info(), file=stderr)
        await bot.close()

    @bot.event
    async def on_message(message: Message):
        if message.author == bot.user:
            return
        elif str(message.author) == su:
            await bot.process_commands(message)

    @bot.event
    async def on_member_join(member: Member):
        # If new guild member is a bot, ignore them
        if not member.bot:
            disc = str(member)
            if disc not in db[KEYS.MMBR]:
                db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: member.id}

        database.dump()

    @bot.event
    async def on_member_update(before: Member, after: Member):
        disc = str(after)   # Discord username can't change

        broles, aroles = set(), set()
        role_map = dict()           # type: Dict[str, Role]
        for role in before.roles:
            rname = obwrole.rolename(role)
            broles.add(rname)
            role_map[rname] = role

        for role in after.roles:
            rname = obwrole.rolename(role)
            aroles.add(rname)
            role_map[rname] = role

        removed = broles.difference(aroles)
        added = aroles.difference(broles)

        for role in removed:
            if role in db[KEYS.ROLE]:
                db[KEYS.ROLE][role][KEYS.MMBR] -= 1
                if not db[KEYS.ROLE][role][KEYS.MMBR]:      # If this was the only member with the role
                    await obwrole.globaldel(role_map[role], role)
                elif disc in db[KEYS.MMBR]:                 # If not, just remove it from all their bnet profiles
                    obwrole.remove(disc, role)

        # All Oberwatch roles are Bot managed and users are not allowed to manually add them, only manually remove
        for role in added:
            if role in db[KEYS.ROLE]:
                await after.remove_roles(role_map[role])
                channel = await getdm(after)
                await channel.send(f"You tried to add {role} to your {str(after.guild)} profile but "
                                   f"do not have permission for this, so the role was removed.")

        database.dump()

    @bot.event
    async def on_guild_role_delete(role: Role):
        rname = obwrole.rolename(role)
        if rname in db[KEYS.ROLE]:
            obwrole.globalrm(rname)

    @bot.event
    async def on_guild_role_update(before: Role, after: Role):
        bname, aname = obwrole.rolename(before), obwrole.rolename(after)

        # If the role wasn't in db before, not a role we care about
        if bname in db[KEYS.ROLE]:
            del db[KEYS.ROLE][bname]
            await sleep(5)      # Give some sleep time for after.members to be updated
            db[KEYS.ROLE][aname] = {KEYS.ID: after.id, KEYS.MMBR: len(after.members)}
            obwrole.rename(bname, aname)

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

        if disc not in db[KEYS.MMBR]:
            db[KEYS.MMBR][disc] = {KEYS.BNET: {}, KEYS.ID: ctx.author.id}

        if bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[KEYS.BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            if ctx.guild is not None:
                await obwrole.update(ctx.guild, disc, bnet)
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
            if bnet not in db[KEYS.MMBR][disc][KEYS.BNET]:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your discord!")
        else:
            battlenet.deactivate(disc, bnet)
            if ctx.guild is not None:
                await obwrole.update(ctx.guild, disc, bnet)
            message = f"You have successfully unlinked {bnet} from your discord!"
            if prim := battlenet.remove(bnet, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.channel.send(message)

        database.dump()

    @bot.command()
    async def primary(ctx: Context, bnet: str):
        disc = str(ctx.author)
        try:
            user_battlenets = db[KEYS.MMBR][disc][KEYS.BNET]
            if bnet not in user_battlenets:
                raise KeyError
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
