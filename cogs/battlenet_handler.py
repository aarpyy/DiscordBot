from discord.ext import commands
from src import battlenet, obwrole
from src.tools import restrict
from src.db_keys import *
from src.config import db


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
            db[BNET][bnet][ROLE] = list(obwrole.generate_roles(bnet))
            await obwrole.update(ctx.guild, disc, bnet)
            await ctx.channel.send(f"Successfully linked {bnet} to your discord!")

    @commands.command(name="battlenet")
    async def _battlenet(self, ctx, bnet):
        await self.account(ctx, bnet, "PC")

    @commands.command()
    async def xbox(self, ctx, bnet):
        await self.account(ctx, bnet, "Xbox")

    @commands.command()
    async def playstation(self, ctx, bnet):
        await self.account(ctx, bnet, "Playstation")

    @commands.command()
    @restrict()
    async def remove(self, ctx, bnet):
        disc = str(ctx.author)
        try:
            if bnet not in db[MMBR][disc][BNET]:
                raise KeyError
        except KeyError:
            await ctx.channel.send(f"{bnet} is not linked to your discord!")
        else:
            battlenet.deactivate(bnet)
            guild = ctx.guild
            if guild is not None:
                await obwrole.update(guild, disc, bnet)
            message = f"You have successfully unlinked {bnet} from your discord!"
            if prim := battlenet.remove(bnet, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.channel.send(message)

    @commands.command()
    @restrict()
    async def setprimary(self, ctx, bnet):
        disc = str(ctx.author)
        if disc not in db or bnet not in db[MMBR][disc][BNET]:
            await ctx.channel.send(f"{bnet} is not linked to your account!")
        elif bnet == db[MMBR][disc][PRIM]:
            await ctx.channel.send(f"{bnet} is already your primary linked account!")
        else:
            db[MMBR][disc][PRIM] = bnet
            await ctx.channel.send(f"{bnet} is your new primary linked account!")

    @commands.command()
    @restrict()
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
