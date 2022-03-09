from os.path import exists, join
from os import system, environ, chdir, getcwd
from sys import platform, stderr
from dotenv import load_dotenv

from discord import Intents, Guild
from discord.ext.commands import Bot


split = "split."


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    bot.run(environ["DISC_TOKEN"])


if __name__ == "__main__":
    global split

    for f in ("comp", "dne", "is_private", "stats"):
        if not exists(join("GET", f)):
            print(f"GET/{f} does not exist", file=stderr)
            exit(1)

    if platform.startswith("darwin"):
        load_dotenv("../.env")
        split += "macos"
    else:
        split += "linux"

    if not exists(join("GET", split)):
        curr = getcwd()
        chdir("GET/split")
        system("make")
        chdir(curr)

