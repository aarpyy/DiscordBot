from replit import db

from discord.ext.commands import Bot
from discord import Guild, Role

import request
from config import KEYS, bot_role_prefix


async def clean_roles(bot: Bot) -> None:
    """
    Deletes all roles given by Bot. Identifies these roles by a specific prefix. Only applicable
    during testing when the prefix is given.

    :param bot: discord bot
    :return: None
    """
    for gld in bot.guilds:                  # type: Guild
        for rle in gld.roles:               # type: Role
            if str(rle).startswith(bot_role_prefix):
                await rle.delete()


def user_data(disc: str, bnet: str) -> None:
    """
    Requests data for battlenet, updating its stats and rank if request was successful. If account is private,
    it is marked as such and data is set to empty. If account DNE or is inaccessible, it is set to inactive
    to be deleted.

    :param disc: discord user
    :param bnet: battlenet
    :return: None
    """
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
