from os import getenv
from src.bot import Oberbot
from cogs import *
from discord import Bot


def main():

    bot = Oberbot()

    bot.add_cog(BattlenetHandler(bot))
    bot.add_cog(TeamInfoHandler(bot))


    # print(f"cogs: {bot.cogs}")

    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
