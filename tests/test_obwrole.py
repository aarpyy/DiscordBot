from src.obwrole import *


def test_format_time():
    assert format_time("36:36:32") == "37h"
    assert format_time("36:32") == "37m"
    assert format_time("32") == "32s"
    assert format_time("") == ""


def test_format_stat():
    assert format_stat("Time Played", "36:36:32") == "37h"
    assert format_stat("Win Percentage", "36") == "36%"
    assert format_stat("random string", "random stat") == "random stat"


async def test_format_role():
    from dotenv import load_dotenv
    from src.config import root
    load_dotenv(root.joinpath(".env"))

    from discord import Intents, Guild
    from discord.ext.commands import Bot
    from os import getenv

    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    bot.run(getenv('DISC_TOKEN'))

    print(f"Logged in as Oberwatch bot")

    guild = None
    gld: Guild
    for gld in bot.guilds:
        if str(gld).startswith("Oberwatch"):
            guild = gld
            break

    if not isinstance(guild, Guild):
        print(f"Guilds: {bot.guilds}")
    else:
        for role in guild.roles:
            print(f"Role: {repr(role)}, {format_role(role)}")

    await bot.logout()
    return


if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    # loop.call_soon(test_format_role)
    # loop.run_forever()
    loop.run_until_complete(test_format_role())
    # loop.close()
