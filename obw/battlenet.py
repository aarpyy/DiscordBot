from typing import Union

from replit import db

from .db_keys import *
from .scrape import platform_url, scrape_play_ow
from .tools import loudprint

# Accessors

def is_active(disc: str, bnet: str):
    return db[MMBR][disc][BNET][bnet][ACTIVE]


def is_hidden(disc: str, bnet: str):
    return db[MMBR][disc][BNET][bnet][HID]


def is_primary(disc: str, bnet: str):
    return db[MMBR][disc][BNET][bnet][PRIM]


def is_private(disc: str, bnet: str):
    return db[MMBR][disc][BNET][bnet][PRIV]


def get_top(superlative: str):
    return max(db[MMBR], key=lambda x: db[MMBR][x][SCORE].get(superlative, 0))


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
    return {PRIM: prim,
            PRIV: priv,
            ACTIVE: True,
            HID: False,
            PTFM: platform,
            RANK: rank,
            STAT: stats,
            ROLE: []}


def clear_index(disc: str, bnet: str):
    db[MMBR][disc][BNET][bnet][STAT] = {}
    db[MMBR][disc][BNET][bnet][RANK] = {}


def deactivate(disc: str, bnet: str):
    clear_index(disc, bnet)
    db[MMBR][disc][BNET][bnet][ACTIVE] = False


def hide(disc: str, bnet: str):
    db[MMBR][disc][BNET][bnet][HID] = True


def show(disc: str, bnet: str):
    db[MMBR][disc][BNET][bnet][HID] = False


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
        db[BNET].append(bnet)
        db[MMBR][disc][BNET][bnet] = create_index(
            not bool(db[MMBR][disc][BNET]), True, pf, {}, {})
    except NameError as exc:    # NameError means DNE, don't add it
        raise NameError("unable to add battlenet") from exc
    except ValueError as exc:   # ValueError means error with data organization or UNIX error
        raise ValueError("unable to add battlenet") from exc
    else:
        db[BNET].append(bnet)
        db[MMBR][disc][BNET][bnet] = create_index(
            not bool(db[MMBR][disc][BNET]), False, pf, rank, stats)


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
        # Try to scrape, 
        ranks, stats = scrape_play_ow(platform_url(db[MMBR][disc][BNET][bnet][PTFM])(bnet))
    except AttributeError:
        db[BNET][bnet][PRIV] = True
        loudprint(f"{bnet} marked as private")
    except NameError or ValueError:
        db[BNET][bnet][ACTIVE] = False
        loudprint(f"{bnet} marked as inactive")
    else:
        db[BNET][bnet][PRIV] = False
    finally:
        db[BNET][bnet][STAT] = stats
        db[BNET][bnet][RANK] = ranks


def remove(bnet: str, disc: str) -> str:
    """
    Removes battlenet from replit database, returning flag of if the user's primary
    account was removed.

    :param bnet: battlenet to be removed
    :param disc: discord user associated with battlenet
    :return: new primary iff account removed was user's old primary, 0 otherwise
    """

    db[BNET].remove_user_role(bnet, )  # Remove from list of all battlenets
    primary = db[MMBR][disc][BNET][bnet][PRIM]
    del db[MMBR][disc][BNET][bnet]

    if primary and db[MMBR][disc][BNET]:       # If it was this user's primary account and they have
        new_prim = next(iter(db[MMBR][disc][BNET]))   # another, make it primary
        db[MMBR][disc][BNET][new_prim][PRIM] = True
        return new_prim
    else:
        return ""
