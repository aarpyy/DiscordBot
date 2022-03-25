from discord.ext import commands
from src.config import db
from src.compositions import get_map, Map, Round
from src.db_keys import *
from src.bot import Oberbot
from discord_slash import SlashContext, cog_ext


class TeamInfoHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="comp",
        description="Prints team composition for a given map and round",
        guild_ids=Oberbot.guild_ids
    )
    async def comp(self, ctx: SlashContext, map_name, round_name=""):
        M, R = get_map(map_name, round_name)
        if M == Map.NoMap:
            await ctx.channel.send(f"{map_name} is not a recognizable map!")
            return

        str_emoji = {emoji.name: str(emoji) for emoji in ctx.guild.emojis}
        if R != Round.All:
            heroes = db[MAP][M.value][R.value]
            composition = [str_emoji.get(e, '') for e in heroes]
            await ctx.channel.send(", ".join(composition))
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
            await ctx.channel.send(message)
