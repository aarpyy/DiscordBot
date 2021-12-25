from replit import db
from config import KEYS

import role
import request


def user_data(disc, bnet):
    ranks, stats = {}, {}
    try:
        ranks, stats = request.main(request.search_url(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PTFM])(bnet))
    except AttributeError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = True
    except NameError or ValueError:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ACTIVE] = False
    else:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PRIV] = False
    finally:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT] = stats
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK] = ranks
