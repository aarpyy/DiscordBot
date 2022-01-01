from replit import db

from scrape import scrape_play_ow, platform_url

from config import Key
from tools import getkey, loudprint

from typing import Union


# Accessors

def is_active(disc: str, bnet: str):
    return db[Key.MMBR][disc][Key.BNET][bnet][Key.ACTIVE]


def is_hidden(disc: str, bnet: str):
    return db[Key.MMBR][disc][Key.BNET][bnet][Key.HID]


def is_primary(disc: str, bnet: str):
    return db[Key.MMBR][disc][Key.BNET][bnet][Key.PRIM]


def is_private(disc: str, bnet: str):
    return db[Key.MMBR][disc][Key.BNET][bnet][Key.PRIV]


def get_top():
    return max(db[Key.MMBR], key=lambda x: db[Key.MMBR][x][Key.SCORE])


# Battlenet methods


def create_index(prim: bool, priv: bool, platform: str, rank: dict, stats: dict) -> dict:
    """
    Creates and returns standard index for battlenet.

    :param prim: whether or not battlenet is user's primary linked account
    :param priv: battlenet's privacy status
    :param platform: platform of battlenet
    :param rank: battlenet's competitive ranks
    :param stats: battlenet's general stats
    :return: battlenet object in db
    """
    return {Key.PRIM: prim,
            Key.PRIV: priv,
            Key.ACTIVE: True,
            Key.HID: False,
            Key.PTFM: platform,
            Key.RANK: rank,
            Key.STAT: stats,
            Key.ROLE: []}


def clear_index(disc: str, bnet: str):
    db[Key.MMBR][disc][Key.BNET][bnet][Key.STAT] = {}
    db[Key.MMBR][disc][Key.BNET][bnet][Key.RANK] = {}


def deactivate(disc: str, bnet: str):
    clear_index(disc, bnet)
    db[Key.MMBR][disc][Key.BNET][bnet][Key.ACTIVE] = False


def hide(disc: str, bnet: str):
    db[Key.MMBR][disc][Key.BNET][bnet][Key.HID] = True


def show(disc: str, bnet: str):
    db[Key.MMBR][disc][Key.BNET][bnet][Key.HID] = False


def add(disc: str, bnet: str, pf: str) -> None:
    """
    Adds battlenet as index to user object with battlenet data as indices in battlenet object.

    :param disc: name of discord user
    :param bnet: name of battlenet
    :param pf: platform of battlenet
    :raises AttributeError: If battlenet is private
    :raises NameError: If battlenet does not exist
    :raises ValueError: If any other error occurred in loading battlenet data
    :return: None
    """
    # Load bnet information in table - if the battlenet is not in list of all battlenets it gets added here
    try:
        rank, stats = scrape_play_ow(platform_url(pf)(bnet))
    except AttributeError:      # AttributeError means private account, still add it
        db[Key.BNET].append(bnet)
        db[Key.MMBR][disc][Key.BNET][bnet] = create_index(
            not bool(db[Key.MMBR][disc][Key.BNET]), True, pf, {}, {})
    except NameError as src:    # NameError means DNE, don't add it
        raise NameError("unable to add battlenet") from src
    except ValueError as src:   # ValueError means error with data organization or UNIX error
        raise ValueError("unable to add battlenet") from src
    else:
        db[Key.BNET].append(bnet)
        db[Key.MMBR][disc][Key.BNET][bnet] = create_index(
            not bool(db[Key.MMBR][disc][Key.BNET]), False, pf, rank, stats)


def update(disc: str, bnet: str) -> None:
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
        ranks, stats = scrape_play_ow(platform_url(db[Key.MMBR][disc][Key.BNET][bnet][Key.PTFM])(bnet))
    except AttributeError:
        db[Key.MMBR][disc][Key.BNET][bnet][Key.PRIV] = True
        loudprint(f"{bnet} marked as private")
    except NameError or ValueError:
        db[Key.MMBR][disc][Key.BNET][bnet][Key.ACTIVE] = False
        loudprint(f"{bnet} marked as inactive")
    else:
        db[Key.MMBR][disc][Key.BNET][bnet][Key.PRIV] = False
    finally:
        db[Key.MMBR][disc][Key.BNET][bnet][Key.STAT] = stats
        db[Key.MMBR][disc][Key.BNET][bnet][Key.RANK] = ranks


def remove(bnet: str, disc: str) -> str:
    """
    Removes battlenet from replit database, returning flag of if the user's primary
    account was removed.

    :param bnet: battlenet to be removed
    :param disc: discord user associated with battlenet
    :return: new primary iff account removed was user's old primary, 0 otherwise
    """

    db[Key.BNET].remove_user_role(bnet, )  # Remove from list of all battlenets
    primary = db[Key.MMBR][disc][Key.BNET][bnet][Key.PRIM]
    del db[Key.MMBR][disc][Key.BNET][bnet]

    if primary and db[Key.MMBR][disc][Key.BNET]:       # If it was this user's primary account and they have
        new_prim = getkey(db[Key.MMBR][disc][Key.BNET])   # another, make it primary
        db[Key.MMBR][disc][Key.BNET][new_prim][Key.PRIM] = True
        return new_prim
    else:
        return ""
