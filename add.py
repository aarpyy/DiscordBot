import request
from config import KEYS
from replit import db
from role import get_bnet_roles


def bnet_index(prim: bool, priv: bool, platform: str, rank: dict, stats: dict):
    return {KEYS.PRIM: prim,
            KEYS.PRIV: priv,
            KEYS.ACTIVE: True,
            KEYS.PTFM: platform,
            KEYS.RANK: rank,
            KEYS.STAT: stats,
            KEYS.ROLE: []}


def battlenet(disc, bnet, pf):
    # At this point, user is in database with primary and all values and in list of all discords

    # Load bnet information in table - if the battlenet is not in list of all battlenets it gets added here
    try:
        url = request.search_url(pf)(bnet)
        print(f"requesting {url}...")
        rank, stats = request.main(url)
        print(f"ranks received: {rank}")
    except AttributeError as src:      # AttributeError means private account, still add it
        print(f"error: {src}")
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
