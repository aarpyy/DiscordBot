from replit import db
from config import KEYS, bot_role_prefix
from os import system
from unidecode import unidecode
from json import load
from discord.ext.commands import Bot
from discord import Guild, Role


def data_categories():
    if not system("./get/category > categories"):
        categ_id = {}
        with open("categories", "r") as infile:
            lines = infile.readlines()

        for line in lines:
            line = line.strip('\n')
            # Only read categories that start with data-id
            if not line.startswith("0x"):
                continue
            else:
                _id, name = line.split('|')
                name = unidecode(name)
                categ_id[_id] = name

        system("rm -f categories")
        return categ_id
    else:
        raise ValueError("UNIX ERROR")


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


def init():
    db[KEYS.MMBR] = {}
    db[KEYS.ROLE] = {}
    db[KEYS.BNET] = []
    with open("categories.json", "r") as infile:
        db[KEYS.CTG] = load(infile)


def clear():
    for key in db:
        del db[key]


def refresh():
    db[KEYS.MMBR] = {}
    db[KEYS.ROLE] = {}
    db[KEYS.BNET] = []
