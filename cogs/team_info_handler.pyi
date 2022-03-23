from discord.ext import commands

class TeamInfoHandler(commands.Cog):
    bot: commands.Bot
    def __init__(self, bot: commands.Bot) -> None: ...
    @staticmethod
    async def comp(ctx: commands.Context, *args: str) -> None: ...
