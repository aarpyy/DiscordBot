from replit import db, Database
db: Database

from .db_keys import *
from .scrape import platform_url, scrape_play_ow
from .tools import loudprint
from .obw_errors import ProfileNotFoundError, PrivateProfileError

# Accessors

def is_active(bnet: str):
    return db[BNET][bnet][ACTIVE]


def is_hidden(bnet: str):
    return db[BNET][bnet][HID]


def is_primary(disc: str, bnet: str):
    return bnet == db[MMBR][disc][PRIM]


def is_private(bnet: str):
    return db[BNET][bnet][PRIV]


def get_top(superlative: str):
    return max(db[MMBR], key=lambda x: db[MMBR][x][SCORE].get(superlative, 0))


def hide(bnet: str):
    db[BNET][bnet][HID] = True


def deactivate(bnet: str):
    # Just used for deactivating account so that update roles removes roles, all active accounts are pending removal
    db[BNET][bnet][ACTIVE] = True


# Battlenet methods


def create_index(bnet: str, pf: str) -> bool:
    """
    Creates and returns standard index for battlenet.

    :param prim: whether or not battlenet is user's primary linked account
    :param priv: battlenet's privacy status
    :param platform: platform of battlenet
    :param rank: battlenet's competitive ranks
    :param stats: battlenet's general stats
    :return: whether or not index was created
    """
    try:
        rank, stats = scrape_play_ow(platform_url(pf)(bnet))
    except PrivateProfileError:
        db[BNET][bnet] = {
            PRIV: True, ACTIVE: True,  HID: False, 
            PTFM: pf, RANK: {}, STAT: {}, ROLE: []
        }
        return True
    except ProfileNotFoundError:
        return False
    else:
        db[BNET][bnet] = {
            PRIV: True, ACTIVE: True,  HID: False, 
            PTFM: pf, RANK: rank, STAT: stats, ROLE: []
        }
        return True


def add(guild: str, disc: str, bnet: str, pf: str) -> bool:
    """
    Adds battlenet as index to user object with battlenet data as indices in battlenet object.

    :param disc: name of discord user
    :param bnet: name of battlenet
    :param pf: platform of battlenet
    :return: if battlenet was added to user
    """
    if create_index(bnet, pf):
        db[GLD][guild][MMBR][disc][BNET].append(bnet)
        if db[GLD][guild][MMBR][disc][PRIM] is None:
            db[GLD][guild][MMBR][disc][PRIM] = bnet
        return True
    else:
        return False


def update(bnet: str) -> None:
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
        # Try to scrape, 
        ranks, stats = scrape_play_ow(bnet, db[BNET][bnet][PTFM])
    except PrivateProfileError:
        db[BNET][bnet][PRIV] = True
        print(f"{bnet} marked as private")
    except ProfileNotFoundError as exc:
        print(f"{exc.profile} not found on playoverwatch.com")
        remove(bnet)
    except ValueError:
        db[BNET][bnet][ACTIVE] = False
        print(f"{bnet} marked as inactive")
    else:
        # If no error raised, then profile not private
        db[BNET][bnet][PRIV] = False
    finally:
        db[BNET][bnet][STAT] = stats
        db[BNET][bnet][RANK] = ranks


def remove(bnet: str, gld: str = "", disc: str = "") -> None:
    """
    Removes battlenet from replit database, returning flag of if the user's primary
    account was removed.

    :param bnet: battlenet to be removed
    :param disc: discord user associated with battlenet
    :return: None
    """

    def remove_from_user(g, d, b):
        db[GLD][g][MMBR][d][BNET].remove(b)
        if bnet == db[GLD][g][MMBR][d][PRIM]:
            if db[GLD][g][MMBR][d][BNET]:
                db[GLD][g][MMBR][d][PRIM] = db[GLD][g][MMBR][d][BNET][0]
            else:
                db[GLD][g][MMBR][d][PRIM] = None


    # TODO: Remove user roles (maybe?)

    del db[BNET][bnet]  # Remove battlenet from database

    # If guild and discord provided, remove directly
    if disc and gld:
        remove_from_user(gld, disc, bnet)

    # Otherwise, just search through all guilds and users, removing from everyone
    else:
        for gld in db[GLD]:
            for disc in db[GLD][gld][MMBR]:
                if bnet in db[GLD][gld][MMBR][disc][BNET]:
                    remove_from_user(gld, disc, bnet)
