from replit import db
from config import KEYS

import role
import request
from replit import db
from discord.ext.commands import Bot
from discord import Guild, Role


async def clean_roles(bot: Bot):
    for gld in bot.guilds:                  # type: Guild
        for rle in gld.roles:               # type: Role
            if str(rle).startswith("--"):
                await rle.delete()


def user_data(disc, bnet):
    ranks, stats = {}, {}
    try:
        ranks, stats = request.main(request.search_url(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PTFM])(bnet))
    except AttributeError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = True
    except NameError or ValueError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE] = False
    else:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = False
    finally:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT] = stats
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK] = ranks
