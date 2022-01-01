from replit import db
from config import Key
from os import system, remove
from unidecode import unidecode
from json import load
from discord.ext.commands import Bot
from discord import Guild
from tools import jsondump, loudprint
import obwrole


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

        remove("categories")
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

    for guild in bot.guilds:            # type: Guild
        for role in await guild.fetch_roles():
            if (rname := obwrole.rolename(role)) in db[Key.ROLE] or role.color == obwrole.obw_color:
                await role.delete()
    loudprint("All roles cleaned")
    dump()


def init():
    db[Key.MMBR] = {}
    db[Key.ROLE] = {}
    db[Key.BNET] = []
    with open("categories.json", "r") as infile:
        db[Key.CTG] = load(infile)


def clear():
    for key in db:
        del db[key]


def refresh():
    db[Key.MMBR] = {}
    db[Key.ROLE] = {}
    db[Key.BNET] = []


def dump():
    with open("userdata.json", "w") as outfile:
        outfile.write(jsondump(db))
