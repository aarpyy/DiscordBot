from os.path import exists, join
from os import system, environ, chdir, getcwd
from sys import platform, stderr
from functools import wraps
from discord import Intents, Guild
from discord.ext.commands import Bot, Context

su = "aarpyy#3360"  # Creator of bot

split = "split."


def restricted(func):
    @wraps(func)
    def new_func(ctx: Context, *args):
        if str(ctx.author) == su:
            return await func(ctx, *args)
        else:
            await ctx.channel.send(f"That command is currently disabled!")

    return new_func


def main():
    intents = Intents.default()
    intents.members = True
    bot = Bot(command_prefix='/', intents=intents, case_insensitive=True)

    @restricted
    @bot.command()
    async def temp(ctx: Context, msg: str):
        await ctx.channel.send(f"Temp called: {msg}")

    bot.run(environ["DISC_TOKEN"])


if __name__ == "__main__":
    global split

    for f in ("comp", "dne", "is_private", "stats"):
        if not exists(join("GET", f)):
            print(f"GET/{f} does not exist", file=stderr)
            exit(1)

    if platform.startswith("darwin"):
        split += "macos"
    else:
        split += "linux"

    if not exists(join("GET", split)):
        curr = getcwd()
        chdir("GET/split")
        system("make")
        chdir(curr)
