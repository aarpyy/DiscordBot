from discord.ext import commands
from discord_slash import SlashContext

class TeamInfoHandler(commands.Cog):
    bot: commands.Bot
    def __init__(self, bot: commands.Bot) -> None: ...
    async def comp(self, ctx: SlashContext, map_name: str, round_name: str = ...) -> None: ...
