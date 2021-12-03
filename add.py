import request
import remove
from config import KEYS
from discord.utils import get
from replit import db
import role


def battlenet(member, bnet, platform):
    if bnet in db:
        # If user in in database and battlenet also is but battlenet isn't linked than this user can't access.
        if bnet not in db[member][KEYS.ALL]:
            raise NameError(f"{bnet} is already linked to another account!")
        else:
            # If it is linked then return. If user in db and battlnet not in then everything is fine.
            return

    # At this point, user is in database with primary and all values and in list of all discords

    # Load bnet information in table - if the battlenet is not in list of all battlenets it gets added here
    try:
        rank, stats = request.main(request.search_url(platform)(bnet))
    except ValueError as src:
        # If player_request was unable to load time played, then this user is either private or DNE

        # Delete data associated with battletag if it is inaccessible
        remove.battlenet(bnet)
        raise ValueError(bnet, "is either private or does not exist") from src
    else:
        db[bnet] = {KEYS.RANK: rank, KEYS.STAT: stats, KEYS.PLTFRM: platform}
        db[KEYS.BNET].append(bnet)
        db[member][KEYS.ALL].append(bnet)
        if db[member][KEYS.PRIM] is None:
            db[member][KEYS.PRIM] = bnet

    async def add_account(ctx, bnet, disc, platform):
        """Adds battlenet to database, adding discord user to database if they are not already
        in. This is the only point where member is added to database unless they were added
        upon joining server."""
        author = ctx.author     # Author of message
        gld = ctx.guild         # Guild message was sent in (if DM, guild is None)

        # If linking battlenet to message author, this can happen outside of guild
        if disc is None or disc == str(author):
            try:
                battlenet(author, bnet, platform)
            except NameError or ValueError as exc:
                await ctx.channel.send(str(exc))
            else:
                if gld is not None:
                    await role.init(gld, author)
        elif gld is None:
            await ctx.channel.send("Unable to link to another account outside of a server!")
        # If linking to account other than author, only allowed for server owner, needs to be inside server
        elif author == gld.owner:
            mmbr = gld.get_member_named(disc)
            if mmbr is None:
                await ctx.channel.send(f"{disc} is not a user in this server!")
                return
            try:
                battlenet(author, bnet, platform)
            except NameError or ValueError as exc:
                await ctx.channel.send(str(exc))
            else:
                await role.init(gld, author)
        else:
            await ctx.channel.send("You don't have permission for this")
