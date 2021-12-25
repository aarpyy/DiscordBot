from replit import db

import request
from config import KEYS
from role import get_bnet_roles


def bnet_index(prim: bool, priv: bool, platform: str, rank: dict, stats: dict) -> dict:
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
            KEYS.PTFM: platform,
            KEYS.RANK: rank,
            KEYS.STAT: stats,
            KEYS.ROLE: []}


def battlenet(disc: str, bnet: str, pf: str) -> None:
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
        db[KEYS.MMBR][disc][KEYS.BNET][bnet] = bnet_index(
            not bool(db[KEYS.MMBR][disc][KEYS.BNET]), True, pf, {}, {})
    except NameError as src:    # NameError means DNE, don't add it
        raise NameError("unable to add battlenet") from src
    except ValueError as src:   # ValueError means error with data organization or UNIX error
        raise ValueError("unable to add battlenet") from src
    else:
        db[KEYS.BNET].append(bnet)
        db[KEYS.MMBR][disc][KEYS.BNET][bnet] = bnet_index(
            not bool(db[KEYS.MMBR][disc][KEYS.BNET]), False, pf, rank, stats)
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(get_bnet_roles(disc, bnet))
