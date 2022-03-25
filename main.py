from os import getenv
from src.bot import Oberbot
from cogs import all_cogs
from discord_slash import SlashCommand


def main():

    bot = Oberbot()

    for cog in all_cogs:
        bot.add_cog(cog(bot))

    SlashCommand(bot, sync_commands=True)

    # print(f"cogs: {bot.cogs}")

    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
