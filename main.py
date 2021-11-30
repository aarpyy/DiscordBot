from discord.ext import commands, tasks
from discord import Intents
import os
import add
from config import KEYS
import request
import db_commands as db_cmd
from replit import db
import retrieve
import remove


SUPERUSER = "aarpyy#3360"


def main():
    intents = Intents.default()
    intents.members = True
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user}.")
        update_loop.start()

    @tasks.loop(hours=1)
    async def update_loop():
        request.update()
        for guild in bot.guilds:
            for user in guild.members:
                if user == bot.user or str(user) not in db:
                    continue
                print("Updating user {0}".format(str(user)))
                await update_roles(guild, str(user))
        print("Updated all accounts")

    @bot.command()
    async def roles(ctx):
        for role in ctx.guild.roles:
            db[KEYS.RLE][str(role)] = role.id
        await ctx.channel.send("Server roles:\n" + '\n'.join(str(e) for e in ctx.guild.roles))
    
    @bot.command()
    async def emojis(ctx):
        for emoji in ctx.guild.emojis:
            await ctx.channel.send("Name: {0}; ID: {1}".format(emoji.name, emoji.id))

    @bot.command(name="db")
    async def _db(ctx, cmd, value=None, *args):
        if str(ctx.author) not in db[KEYS.ADM]:
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
    async def set(ctx, key, bnet):
        author = str(ctx.author)
        if key == 'primary':
            if bnet == db[author][KEYS.PRM]:
                await ctx.channel.send(f"{bnet} is already your primary!")
            elif bnet in db[author][KEYS.ALL]:
                db[author][KEYS.PRM] = bnet
                await ctx.channel.send(f"Successfully made {bnet} your new primary")
            else:
                await ctx.channel.send(f"{bnet} is not linked to your discord. Link it first!")
        else:
            await ctx.channel.send("Incorrect /set usage. Try using /set primary bnet to set a primary battlenet.")

    @bot.command(name="remove")
    async def _remove(ctx, value):
        print(f"All discords: {db[KEYS.DSC]}")
        author = str(ctx.author)
        print(f"value: {value}")
        print(f"bnet: {db[KEYS.BNT]}")
        print(f"disc: {db[KEYS.DSC]}")
        if value in db[KEYS.BNT] or value in db:
            if author == SUPERUSER or value in db[author][KEYS.ALL]:
                message = remove.battlenet(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("{0} is not linked to your discord so you can't remove it".format(value))
        elif value in db[KEYS.DSC] or value in db:
            if value == author or author == SUPERUSER:
                message = remove.member(value)
                await ctx.channel.send(message)
            else:
                await ctx.channel.send("You are not able to remove {0} from the database, sorry!".format(value))
        else:
            await ctx.channel.send("Invalid remove options.\nUsage: /remove (battlenet or discord username)")

    # Helper function to retrieve user data and send response message
    async def send_info(ctx, user, key=None):
        if user in db[KEYS.DSC]:
            await ctx.channel.send(retrieve.player_stats(db[user][KEYS.PRM], _key=key))
        elif user in db[KEYS.BNT]:
            await ctx.channel.send(retrieve.player_stats(user, _key=key))
        elif user is None:
            author = str(ctx.author)
            if author in db:
                bnet = db[author][KEYS.PRM]
                await ctx.channel.send(retrieve.player_stats(bnet, _key=key))
            else:
                await ctx.channel.send('{0} does not have any linked battlenet accounts'.format(author))
        else:
            await ctx.channel.send('Unable to get info on {0}'.format(user))

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
            for user in ctx.guild.members:
                await update_roles(ctx.guild, user)
            await ctx.channel.send("{0} Battlenet accounts updated".format(len(db[KEYS.BNT])))
        elif user in db[KEYS.BNT]:
            request.update(user)
            await ctx.channel.send("{0} updated".format(user))
        else:
            await ctx.channel.send("{0} not linked Battlenet".format(user))

    async def update_roles(guild, user):
        player_roles = retrieve.user_roles(user)

        if isinstance(user, str):
            user = guild.get_member_named(user)
        if user is None:
            return
        # Create all new roles
        for role in player_roles:
            role_obj = await add.role(guild, player_roles[role])

            if role_obj not in user.roles:
                print("Giving {0} role to {1}...".format(player_roles[role], str(user)))
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
                if ctx.guild is not None:
                    await update_roles(ctx.guild, user)
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
            await ctx.channel.send("Your primary linked battlenet account is " + db[usern][KEYS.PRM])
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
