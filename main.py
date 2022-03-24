from os import getenv
from src.bot import Oberbot
from src.config import db
from src.compositions import get_map, Map, Round
from src.db_keys import *
from discord_slash import SlashCommand, SlashContext
from cogs import all_cogs


def main():

    bot = Oberbot()

    slash = SlashCommand(bot, sync_commands=True)

    # for cog in all_cogs:
    #     bot.add_cog(cog(bot))

    @slash.slash(
        name="comp",
        description="Prints team composition for a given map",
        guild_ids=bot.guild_ids
    )
    async def comp(ctx: SlashContext, map_name, round_name=""):
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
            for r in db[MAP][M.value]:  # type: str

                #  current team composition and its readable string (with emojis)
                heroes = db[MAP][M.value][r]
                composition = [str_emoji.get(e, '') for e in heroes]

                # Convert round name into nicer string
                round_name = " ".join(s.capitalize() for s in r.split('-'))

                # Append to message
                message += f"{round_name}:  " + " ".join(composition) + "\n"
            await ctx.channel.send(message)

    # Log in to bot using token from replit env and run
    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
