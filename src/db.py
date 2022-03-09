from os import remove, system
from unidecode import unidecode

from replit import db

from tables import *


def data_categories():

    if not system("curl -s 'https://playoverwatch.com/en-us/career/pc/Aarpyy-1975/' | "
                  "./GET/split.macos | "
                  "sed -n -E 's/<option value=[\"](.*)[\"] option-id=[\"](.*)[\"]>.*$/\\1|\\2/p' > categories"):
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


def init_db():
    db[GUILDS] = {}
    db[BNET] = {}
    db[BOT_ROLES] = {}
    db[CATEG] = data_categories()


def create_guild_index(guild: str):
    if guild in db[GUILDS]:
        raise KeyError("Guild already exists in database!")
    else:
        db[GUILDS][guild] = {}


def create_user_index(
        guild: str,     # Guild that user belongs to
        user: str       # Discord username of index
):
    if guild not in db[GUILDS]:
        raise KeyError("Guild does not exist in database!")

    # This function ONLY adds new users, and raises error if they already exist
    elif user in db[GUILDS][guild][USERS]:
        raise KeyError("User already exists in database!")
    else:
        db[GUILDS][guild][USERS][user] = {
            BNET: {},
            USR_ROLE: [],
        }


def create_battlenet_index(
        guild: str,
        user: str,
        battlenet: str,
        stats: dict,
        *,
        rank: dict = None,
        is_primary: bool = False,
        is_private: bool = False,
        platform: str = "PC"
):
    if not stats:
        raise ValueError("Battlenet does not have stats")
    elif guild not in db[GUILDS]:
        raise KeyError("Guild does not exist in database!")
    elif user not in db[GUILDS][guild][USERS]:
        raise KeyError("User does not exist in database!")
    elif battlenet in db[BNET]:
        if user == db[BNET][battlenet][USERS]:
            raise KeyError("Battlenet already exists in database for this user!")
        else:
            raise KeyError("Battlenet exists in database for another user!")
    else:
        db[GUILDS][guild][USERS][user][BNET].append(battlenet)

        db[BNET][battlenet] = {
            USERS: user,
            STATS: stats,
            RANK: {} if rank is None else rank,
            IS_PRIM: is_primary,
            IS_PRIV: is_private,
            PLATFORM: platform,
            USR_ROLE: [],
            IS_ACTIVE: True
        }


def remove_guild(guild: str):
    if guild not in db[GUILDS]:
        raise KeyError("Guild does not exist in database!")
    else:
        del db[GUILDS][guild]


def remove_user(guild: str, user: str):
    if guild not in db[GUILDS]:
        raise KeyError("Guild does not exist in database!")
    elif user not in db[GUILDS][guild][USERS]:
        raise KeyError("User does not exist in database!")
    else:
        del db[GUILDS][guild][USERS][user]


def remove_battlenet_index(
        guild: str,
        user: str,
        battlenet: str
):
    pass
