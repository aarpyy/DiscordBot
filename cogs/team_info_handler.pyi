from discord.ext import commands
from discord import Bot
from discord.commands import ApplicationContext

class TeamInfoHandler(commands.Cog):
    bot: Bot
    def __init__(self, bot: Bot) -> None: ...
    async def comp(self, ctx: ApplicationContext, map_name: str, round_name: str = ...) -> None: ...
