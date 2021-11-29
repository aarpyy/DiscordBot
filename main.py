from discord.ext import commands
from discord.utils import get
import os
from add_member import add
from config import *
from replit import db
from retrieve import get_roles, send_info
from remove import remove_user, remove_bnet

SUPERUSER = "aarpyy#3360"


def main():
    bot = commands.Bot(command_prefix='/')

    @bot.event
    async def on_ready():
        print(f"logged in as {bot.user}")

    @bot.command()
    async def roles(ctx):
        await ctx.channel.send("Server roles:\n" + '\n'.join(str(e) for e in bot.guilds[0].roles))
    
    @bot.command()
    async def clear_db(ctx):
        try:
            constant = (key_ad, key_bn, key_dsc, 'ranks', 'roles')
            for key in db:
                if key not in constant:
                    del db[key]
            db[key_bn] = []
            db[key_dsc] = []
        except KeyError:
            await ctx.channel.send("An error occurred")
        else:
            await ctx.channel.send("Database cleared!")

    @bot.command()
    async def remove(ctx, value, user=None):
        author = str(ctx.author)
        if value in db[key_bn]:
            if author == SUPERUSER or value in db[author][key_all]:
                message = remove_bnet(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("{0} is not linked to your discord so you can't remove it".format(value))
        elif value in db[key_dsc]:
            if value == author or author == SUPERUSER:
                message = remove_user(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("You are not able to remove {0} from the database, sorry!".format(value))
        else:
            await ctx.channel.send("Invalid remove options.\nUsage: /remove (battlenet or discord username)")

    @bot.command(name='add')
    async def add_entry(ctx, key, value, dtype_key=None, dtype_value=None):
        if str(ctx.author) in db[key_ad]:
            if dtype_key is not None:
                key = dtype_key(key)
            if dtype_value is not None:
                value = dtype_value(value)
            db[key] = value
            await ctx.channel.send("Successfully added {0}: {1} to the database".format(key, value))
        else:
            await ctx.channel.send("Must be a database admin to add values")

    @bot.command(name='get')
    async def get_entry(ctx, key):
        if str(ctx.author) in db[key_ad]:
            if key in db:
                await ctx.channel.send(str(db[key]))
            else:
                await ctx.channel.send("Invalid database key: {0}".format(key))
        else:
            await ctx.channel.send("Must be a database admin to get values from db")

    @bot.command()
    async def add_admin(ctx, username):
        if str(ctx.author) == SUPERUSER:
            db[key_ad].append(username)
            await ctx.channel.send("Successfully added {0} as a database admin".format(username))
        else:
            await ctx.channel.send("Must be database superuser to change add admins")

    @bot.command(brief="Shows player's competitive rank(s) for this season")
    async def rank(ctx, user=None):
        await send_info(ctx, user, 'rank')

    @bot.command(brief="Shows player's top 10 most player heroes")
    async def time(ctx, user=None):
        await send_info(ctx, user, 'time')

    @bot.command(brief="Shows all player stats")
    async def stats(ctx, user=None):
        await send_info(ctx, user)

    async def update_roles(guild, user):
        user_roles = get_roles(str(user))
        to_add = user_roles.difference(set(str(e) for e in guild.roles))
        for role in to_add:
            print("Adding {0} role to server...".format(role))
            await guild.create_role(name=role)
        for role in user_roles:
            role_obj = get(guild.roles, name=role)
            print("Giving {0} role to {1}...".format(role, str(user)))
            await user.add_roles(role_obj)

    @bot.command(brief="Connects given battlenet to user's Discord")
    async def battlenet(ctx, bnet, disc=None):
        try:
            add(disc or str(ctx.author), bnet)
        except ValueError:
            await ctx.channel.send("{0} either private or does not exist".format(bnet))
        except KeyError:
            await ctx.channel.send("{0} is linked with another discord user".format(bnet))
        else:
            if disc is not None:
                user = bot.get_user(disc)
            else:
                user = ctx.author
            print('User: {0}'.format(str(user)))
            print('Guild: {0}'.format(str(ctx.guild)))
            await update_roles(ctx.channel.guild, user)
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
