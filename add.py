import request
import remove
from config import KEYS
from replit import db


def battlenet(member, bnet, platform):
    # At this point, user is in database with primary and all values and in list of all discords

    # Load bnet information in table - if the battlenet is not in list of all battlenets it gets added here
    try:
        rank, stats = request.main(request.search_url(platform)(bnet))
    except ValueError as src:
        # If player_request was unable to load time played, then this user is either private or DNE

        # Delete data associated with battletag if it is inaccessible
        remove.battlenet(bnet, member)
        raise ValueError(bnet, "is either private or does not exist") from src
    else:
        db[bnet] = {KEYS.RANK: rank, KEYS.STAT: stats, KEYS.PLTFRM: platform}
        db[KEYS.BNET].append(bnet)
        db[member][KEYS.ALL].append(bnet)
        if db[member][KEYS.PRIM] is None:
            db[member][KEYS.PRIM] = bnet


def user_index():
    return {KEYS.PRIM: None, KEYS.ALL: [], KEYS.ROLE: []}

