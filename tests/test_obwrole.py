import pytest
from src.config import db
from discord import Guild
from src.roles import *
from src.bot import Oberbot
from cogs import all_cogs
from os import getenv


class TestRoles:
    bot = Oberbot()

    for cog in all_cogs:
        bot.add_cog(cog(bot))

    # Log in to bot using token from replit env and run
    bot.run(getenv('DISC_TOKEN'))

    def test_format_time(self):
        assert format_time("36:36:32") == "37h"
        assert format_time("36:32") == "37m"
        assert format_time("32") == "32s"
        assert format_time("") == ""

    def test_format_stat(self):
        assert format_stat("Time Played", "36:36:32") == "37h"
        assert format_stat("Win Percentage", "36") == "36%"
        assert format_stat("random string", "random stat") == "random stat"

    def test_format_role(self):

        assert TestRoles.bot is not None

        guild = None
        gld: Guild
        for gld in TestRoles.bot.guilds:
            if str(gld).startswith("Oberwatch"):
                guild = gld
                break

        assert isinstance(guild, Guild)

        for role in guild.roles:
            if role.mentionable:
                assert format_role(role) == f"@m{str(role)}"
            else:
                assert format_role(role) == f"--{str(role)}"

        # Until I understand async tests, this is how I stop the test running assuming nothing before failed
        exit(0)


if __name__ == "__main__":
    pass
