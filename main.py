from discord.ext import commands, tasks
from discord.utils import get
from discord import Intents
import os
import add
from config import KEYS as k
import request
import db_commands as db_cmd
from replit import db
from retrieve import get_roles, send_info
from remove import remove_user, remove_bnet


SUPERUSER = "aarpyy#3360"


def main():
    intents = Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
        update_loop.start()

    @tasks.loop(minutes=1)
    async def update_loop():
        request.update()
        for guild in bot.guilds:
            for user in guild.members:
                if user == bot.user or str(user) not in db:
                    continue
                print("Updating user {0}".format(str(user)))
                await update_roles(guild, user)
        print("Updated all accounts")

    @bot.command()
    async def roles(ctx):
        for role in ctx.guild.roles:
            db[k.RLE][str(role)] = role.id
        await ctx.channel.send("Server roles:\n" + '\n'.join(str(e) for e in ctx.guild.roles))
    
    @bot.command()
    async def emojis(ctx):
        for emoji in ctx.guild.emojis:
            await ctx.channel.send("Name: {0}; ID: {1}".format(emoji.name, emoji.id))

    @bot.command(name="db")
    async def _db(ctx, cmd, value, *args):
        if str(ctx.author) not in db[k.ADM]:
            await ctx.channel.send("You must be a database administrator to run a /db command")
            return

        if cmd == 'clear':
            await ctx.channel.send(db_cmd.clear())
        elif cmd == 'add':
            await ctx.channel.send(db_cmd.add(value, *args))
        elif cmd == 'get':
            await ctx.channel.send(db_cmd.get(value, *args))
        elif cmd == 'remove':
            await ctx.channel.send(db_cmd.remove(value, *args))
        elif cmd == 'admin':
            await ctx.channel.send(db_cmd.admin(value))
        elif cmd in ('cmds', 'commands'):
            await ctx.channel.send("Available database commands:\nclear\nadd\nget\nremove\nadmin")
        else:
            await ctx.channel.send("Unrecognized database command")

    @bot.command()
    async def remove(ctx, value):
        author = str(ctx.author)
        if value in db[k.BNT]:
            if author == SUPERUSER or value in db[author][k.ALL]:
                message = remove_bnet(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("{0} is not linked to your discord so you can't remove it".format(value))
        elif value in db[k.DSC]:
            if value == author or author == SUPERUSER:
                message = remove_user(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("You are not able to remove {0} from the database, sorry!".format(value))
        else:
            await ctx.channel.send("Invalid remove options.\nUsage: /remove (battlenet or discord username)")

    @bot.command(brief="Shows player's competitive rank(s) for this season")
    async def rank(ctx, user=None):
        await send_info(ctx, user, 'rank')

    @bot.command(brief="Shows player's top 10 most player heroes")
    async def time(ctx, user=None):
        await send_info(ctx, user, 'time')

    @bot.command(brief="Shows all player stats")
    async def stats(ctx, user=None):
        await send_info(ctx, user)

    @bot.command(brief="Updates player stats for all linked battlenets")
    async def update(ctx, user=None):
        if user is None:
            request.update()
            await ctx.channel.send("{0} Battlenet accounts updated".format(len(db[k.BNT])))
        elif user in db[k.BNT]:
            request.update(user)
            await ctx.channel.send("{0} updated".format(user))
        else:
            await ctx.channel.send("{0} not linked Battlenet".format(user))

    async def update_roles(guild, user):
        user_roles = get_roles(str(user))

        # Create all new roles
        for role in user_roles:
            role_obj = await add.role(guild, user_roles[role])

            if role_obj not in user.roles:
                print("Giving {0} role to {1}...".format(user_roles[role], str(user)))
                await user.add_roles(role_obj)

    @bot.command(brief="Connects given battlenet to user's Discord")
    async def battlenet(ctx, bnet, disc=None):
        try:
            if disc is not None:
                user = disc
                if str(ctx.author) != SUPERUSER:
                    await ctx.channel.send("You don't have permission for this. Nice try!")
                    return
            else:
                user = str(ctx.author)

            add.battlenet(user, bnet)
        except ValueError:
            await ctx.channel.send("{0} either private or does not exist".format(bnet))
        except KeyError:
            await ctx.channel.send("{0} is linked with another discord user".format(bnet))
        else:
            try:
                await update_roles(ctx.channel.guild, user)
            except ValueError:
                await ctx.channel.send("An error occurred in assigning you roles. Try /remove battlenet and re-adding"
                                       " it. If this doesn't fix it, probably message aarpyy")
            if disc is None:
                await ctx.channel.send("Successfully linked {0} to your Discord!".format(bnet))
            else:
                await ctx.channel.send("Successfully linked {0} to {1}!".format(bnet, disc))

    @bot.command(brief='Shows primary battlenet account (if any)')
    async def primary(ctx):
        usern = str(ctx.author)
        if usern in db:
            await ctx.channel.send("Your primary linked battlenet account is " + db[usern]['primary'])
        else:
            await ctx.channel.send(
                "You have not yet linked a battlenet account!\nRun /battlenet followed by your full battletag to link.")

    @bot.command(brief='Shows list of linked battlenet accounts (if any)')
    async def accounts(ctx):
        usern = str(ctx.author)
        if usern in db:
            await ctx.channel.send("You have linked " + ', '.join(db[usern]['all']))
        else:
            await ctx.channel.send(
                "You have not yet linked a battlenet account!\nRun /battlenet followed by your full battletag to link.")

    @bot.command(brief='Shows latency in connection to the Bot')
    async def latency(ctx):
        await ctx.channel.send("{0:.0f}ms".format(bot.latency * 1000))

    # Naming this function commands conflicts with import commands, so this uses a different name and adjusts the command name to /commands in bot.command()
    @bot.command(name='commands', brief='Shows list of valid commands')
    async def display_commands(ctx):
        message = "Available commands:\n" + '\n'.join('/' + str(e) for e in bot.commands)
        await ctx.channel.send(message)

    # Log in to bot using token from replit env and run
    bot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
