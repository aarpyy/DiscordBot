from os import getenv
from src.bot import Oberbot
from cogs import all_cogs


def main():

    bot = Oberbot()

    for cog in all_cogs:
        bot.add_cog(cog(bot))

    # Log in to bot using token from replit env and run
    bot.run(getenv('DISC_TOKEN'))


if __name__ == "__main__":
    main()
