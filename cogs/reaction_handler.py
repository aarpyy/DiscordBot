from discord import Member, Guild, Message
from discord.ext import commands

import asyncio

from src.bot import Oberbot
from src import messaging, roles
from src.db_keys import *
from src.config import db


class ReactionHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def on_reaction_add(reaction, user):
        message = reaction.message  # type: Message
        channel = message.channel
        guild = message.guild
        author = message.author

        # Check to confirm that reaction was in channel of guild we are interested in
        if isinstance(author, Member) and isinstance(guild, Guild) and messaging.valid_reaction(reaction) and \
                messaging.valid_channel(channel):
            emoji = reaction.emoji
            print(f"Emoji: {repr(emoji)} (is custom: {reaction.custom_emoji})")
            print(f"Reaction: {repr(reaction)}")
            await messaging.log_reaction(author, reaction)

        print("Database dumped")

    @staticmethod
    async def on_member_join(member):
        # If new guild member is a bot, ignore them
        if not member.bot:
            disc = str(member)
            if disc not in db[MMBR]:
                db[MMBR][disc] = {ID: member.id, RXN: {}, SCORE: {}, BNET: {}}

    @staticmethod
    async def on_guild_role_delete(role):
        rname = roles.format_role(role)

        # If the bot removed this role, then rname will already be deleted, this is just if another user deletes role
        if rname in db[ROLE]:
            roles.remove_role(rname)

    @staticmethod
    async def on_guild_role_update(before, after):
        bname, aname = roles.format_role(before), roles.format_role(after)

        # TODO: This might not need to be done like this, since role update might not mean user count changes!

        # If the role wasn't in db before, not a role we care about
        if bname in db[ROLE]:
            del db[ROLE][bname]
            await asyncio.sleep(5)  # Give some sleep time for after.members to be updated
            db[ROLE][aname] = {ID: after.id, MMBR: len(after.members)}
            roles.rename_role(bname, aname)
