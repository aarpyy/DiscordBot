from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from src import battlenet, roles
from src.utils import restrict
from src.db_keys import *
from src.config import db
from src.bot import Oberbot


class BattlenetHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @restrict()
    async def account(self, ctx, bnet, platform):
        """
        Attempts to link battlenet account to user's discord.

        :param ctx: Context of command
        :param bnet: battlenet
        :param platform: platform of battlenet
        :return: None
        """
        disc = str(ctx.author)

        # If user not in database, add them
        if disc not in db[MMBR]:
            db[MMBR][disc] = {ID: ctx.author.id, BNET: [], PRIM: None, RXN: {}, SCORE: {}}

        if bnet in db[MMBR][disc][BNET]:
            await ctx.channel.send(f"{bnet} is already linked to your account!")
        elif bnet in db[BNET]:
            await ctx.channel.send(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            db[BNET][bnet][ROLE] = list(roles.generate_roles(bnet))
            await roles.update_user_roles(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

    @cog_ext.cog_slash(
        name="battlenet",
        description="Links Battlenet account to your discord",
        guild_ids=Oberbot.guild_ids
    )
    async def _battlenet(self, ctx, bnet):
        await self.account(ctx, bnet, "PC")

    @cog_ext.cog_slash(
        description="Links Xbox Overwatch account to your discord",
        guild_ids=Oberbot.guild_ids
    )
    async def xbox(self, ctx, xblive):
        await self.account(ctx, xblive, "Xbox")

    @cog_ext.cog_slash(
        description="Links Playstation Overwatch account to your discord",
        guild_ids=Oberbot.guild_ids
    )
    async def playstation(self, ctx, psn):
        await self.account(ctx, psn, "Playstation")

    @cog_ext.cog_slash(
        description="Unlinks account from your discord",
        guild_ids=Oberbot.guild_ids
    )
    @restrict()
    async def remove(self, ctx, acc):
        disc = str(ctx.author)
        try:
            if acc not in db[MMBR][disc][BNET]:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{acc} is not linked to your discord!")
        else:
            battlenet.deactivate(acc)
            guild = ctx.guild
            if guild is not None:
                await roles.update_user_roles(guild, disc, acc)
            message = f"You have successfully unlinked {acc} from your discord!"
            if prim := battlenet.remove(acc, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.channel.send(message)

    @cog_ext.cog_slash(
        description="Sets a alt account to your primary",
        guild_ids=Oberbot.guild_ids
    )
    @restrict()
    async def setprimary(self, ctx, acc):
        disc = str(ctx.author)
        if disc not in db or acc not in db[MMBR][disc][BNET]:
            await ctx.channel.send(f"{acc} is not linked to your account!")
        elif acc == db[MMBR][disc][PRIM]:
            await ctx.channel.send(f"{acc} is already your primary linked account!")
        else:
            db[MMBR][disc][PRIM] = acc
            await ctx.channel.send(f"{acc} is your new primary linked account!")

    @commands.command()
    async def accounts(self, ctx):
        disc = str(ctx.author)
        if disc not in db[MMBR] or not db[MMBR][disc][BNET]:
            await ctx.channel.send("You don't have any linked battlenets!")
        else:
            message = ", ".join(b + " (primary) " if db[MMBR][disc][PRIM] == b else b for b in db[MMBR][disc][BNET])
            await ctx.channel.send("Linked accounts:\n" + message)

    # Temp commands

    @commands.command()
    async def clearroles(self, *args):
        for r in db[ROLE]:
            del db[ROLE][r]

    @commands.command()
    async def clearmembers(self, *args):
        for a in db[MMBR]:
            del db[MMBR][a]
