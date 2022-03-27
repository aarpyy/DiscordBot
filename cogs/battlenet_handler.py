from discord.commands import slash_command, command
from discord.ext import commands
from src import battlenet, roles
from src.utils import restrict
from src.db_keys import *
from src.config import db, guild_ids
from src.ranks import rank_names, get_rank


class BattlenetHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @restrict()
    @staticmethod
    async def account(ctx, bnet, platform):
        """
        Attempts to link battlenet account to user's discord.

        :param ctx: Context of command
        :param bnet: battlenet
        :param platform: platform of battlenet
        :return: None
        """
        disc = str(ctx.author)
        bnet = bnet.strip()

        # If user not in database, add them
        if disc not in db[MMBR]:
            db[MMBR][disc] = {ID: ctx.author.id, BNET: [], PRIM: None, RXN: {}, SCORE: {}}

        if bnet in db[MMBR][disc][BNET]:
            await ctx.respond(f"{bnet} is already linked to your account!")
        elif bnet in db[BNET]:
            await ctx.respond(f"{bnet} is already linked to another user!")
        else:
            battlenet.add(disc, bnet, platform)
            db[BNET][bnet][ROLE] = list(roles.generate_roles(bnet))
            await roles.update_user_roles(ctx.guild, disc, bnet)
            await ctx.respond(f"Successfully linked {bnet} to your discord!")

    @slash_command(
        name="battlenet",
        description="Links Battlenet account to your discord",
        guild_ids=guild_ids
    )
    async def _battlenet(self, ctx, bnet):
        await self.account(ctx, bnet, "PC")

    @slash_command(
        description="Links Xbox Overwatch account to your discord",
        guild_ids=guild_ids
    )
    async def xbox(self, ctx, xblive):
        await self.account(ctx, xblive, "Xbox")

    @slash_command(
        description="Links Playstation Overwatch account to your discord",
        guild_ids=guild_ids
    )
    async def playstation(self, ctx, psn):
        await self.account(ctx, psn, "Playstation")

    @slash_command(
        description="Unlinks account from your discord",
        guild_ids=guild_ids
    )
    @restrict()
    async def remove(self, ctx, acc):
        disc = str(ctx.author)
        try:
            if acc not in db[MMBR][disc][BNET]:
                raise KeyError
        except KeyError:
            await ctx.respond(f"{acc} is not linked to your discord!")
        else:
            battlenet.deactivate(acc)
            guild = ctx.guild
            if guild is not None:
                await roles.update_user_roles(guild, disc, acc)
            message = f"You have successfully unlinked {acc} from your discord!"
            if prim := battlenet.remove(acc, disc):
                message += f"\n\nYour new primary account is {prim}"
            await ctx.respond(message)

    @slash_command(
        description="Sets a alt account to your primary",
        guild_ids=guild_ids
    )
    @restrict()
    async def setprimary(self, ctx, acc):
        disc = str(ctx.author)
        if disc not in db or acc not in db[MMBR][disc][BNET]:
            await ctx.respond(f"{acc} is not linked to your account!")
        elif acc == db[MMBR][disc][PRIM]:
            await ctx.respond(f"{acc} is already your primary linked account!")
        else:
            db[MMBR][disc][PRIM] = acc
            await ctx.respond(f"{acc} is your new primary linked account!")

    @slash_command(
        description="Lists all linked accounts for discord user",
        guild_ids=guild_ids
    )
    async def accounts(self, ctx):
        disc = str(ctx.author)
        if disc not in db[MMBR] or not db[MMBR][disc][BNET]:
            await ctx.respond("You don't have any linked battlenets!")
        else:
            message = ", ".join(b + " (primary) " if db[MMBR][disc][PRIM] == b else b for b in db[MMBR][disc][BNET])
            await ctx.respond("Linked accounts:\n" + message)

    @slash_command(
        description="Show roles a user has",
        guild_ids=guild_ids
    )
    @restrict()
    async def showroles(self, ctx):
        disc = str(ctx.author)
        if disc not in db[MMBR] or not any(db[BNET][b][ROLE] for b in db[MMBR][disc][BNET]):
            await ctx.respond("You don't have any roles!")
        else:
            message = "\n".join(f"{b}: {[r for r in db[BNET][b][ROLE]]}" for b in db[MMBR][disc][BNET])
            await ctx.respond("Roles:\n" + message)

    @slash_command(
        description="Shows stats for Overwatch account",
        guild_ids=guild_ids
    )
    @restrict()
    async def rank(self, ctx, bnet="PRIMARY"):
        if bnet == "PRIMARY":
            disc = str(ctx.author)
            if disc not in db[MMBR] or db[MMBR][disc][PRIM] is None:
                await ctx.respond("You haven't linked any battlenets yet!")
            else:
                bnet = db[MMBR][disc][PRIM]
        if bnet in db[BNET]:

            # If can find emojis that correspond to ranks, load them into dict
            if ctx.guild is not None:
                rank_emojis = {e.name: str(e) for e in ctx.guild.emojis if e.name in rank_names}
            else:
                rank_emojis = {}

            # Send back message containing "Rank name, rank, rank emoji" for each role
            message = "\n".join((
                f"{r.capitalize()}: " +
                rank_emojis.get(get_rank(int(db[BNET][bnet][RANK][r])).value, " ") +
                f"{db[BNET][bnet][RANK][r]}"
                for r in db[BNET][bnet][RANK]
            ))
            await ctx.respond(message)
        else:
            await ctx.respond("Battlenet not in database!")

    # Temp commands

    @command()
    async def clearroles(self, ctx):
        for r in db[ROLE]:
            del db[ROLE][r]

    @command()
    async def clearmembers(self, ctx):
        for a in db[MMBR]:
            del db[MMBR][a]
