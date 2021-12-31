from replit import db

import request

from config import KEYS
from tools import getkey, loudprint

from typing import Union


# Accessors

def is_active(disc: str, bnet: str):
    return db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE]


def is_hidden(disc: str, bnet: str):
    return db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.HID]


def is_primary(disc: str, bnet: str):
    return db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIM]


def is_private(disc: str, bnet: str):
    return db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV]


def clear_index(disc: str, bnet: str):
    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT] = {}
    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK] = {}


def deactivate(disc: str, bnet: str):
    clear_index(disc, bnet)
    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE] = False


def hide(disc: str, bnet: str):
    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.HID] = True


def show(disc: str, bnet: str):
    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.HID] = False


def get_top():
    return max(db[KEYS.MMBR], key=lambda x: db[KEYS.MMBR][x][KEYS.SCORE])


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
    return {KEYS.PRIM: prim,
            KEYS.PRIV: priv,
            KEYS.ACTIVE: True,
            KEYS.HID: False,
            KEYS.PTFM: platform,
            KEYS.RANK: rank,
            KEYS.STAT: stats,
            KEYS.ROLE: []}


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
        rank, stats = request.main(request.search_url(pf)(bnet))
    except AttributeError:      # AttributeError means private account, still add it
        db[KEYS.BNET].append(bnet)
        db[KEYS.MMBR][disc][KEYS.BNET][bnet] = create_index(
            not bool(db[KEYS.MMBR][disc][KEYS.BNET]), True, pf, {}, {})
    except NameError as src:    # NameError means DNE, don't add it
        raise NameError("unable to add battlenet") from src
    except ValueError as src:   # ValueError means error with data organization or UNIX error
        raise ValueError("unable to add battlenet") from src
    else:
        db[KEYS.BNET].append(bnet)
        db[KEYS.MMBR][disc][KEYS.BNET][bnet] = create_index(
            not bool(db[KEYS.MMBR][disc][KEYS.BNET]), False, pf, rank, stats)


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
        ranks, stats = request.main(request.search_url(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PTFM])(bnet))
    except AttributeError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = True
        loudprint(f"{bnet} marked as private")
    except NameError or ValueError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE] = False
        loudprint(f"{bnet} marked as inactive")
    else:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = False
    finally:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT] = stats
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK] = ranks


def remove(bnet: str, disc: str) -> str:
    """
    Removes battlenet from replit database, returning flag of if the user's primary
    account was removed.

    :param bnet: battlenet to be removed
    :param disc: discord user associated with battlenet
    :return: new primary iff account removed was user's old primary, 0 otherwise
    """

    db[KEYS.BNET].remove(bnet)                      # Remove from list of all battlenets
    primary = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIM]
    del db[KEYS.MMBR][disc][KEYS.BNET][bnet]

    if primary and db[KEYS.MMBR][disc][KEYS.BNET]:       # If it was this user's primary account and they have
        new_prim = getkey(db[KEYS.MMBR][disc][KEYS.BNET])   # another, make it primary
        db[KEYS.MMBR][disc][KEYS.BNET][new_prim][KEYS.PRIM] = True
        return new_prim
    else:
        return ""
