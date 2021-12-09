from replit import db
from config import KEYS
from functools import reduce


# Converts time (in seconds) to list of time intervals in descending magnitudes of time
def sec_to_t(t):
    time = []
    while t:
        t, r = divmod(t, 60)
        time.append(r)
    return time[::-1]


# Converts time (in seconds) into a string to display time
def seconds_to_time(t):
    time = sec_to_t(t)
    if len(time) == 3:
        return "{0}h, {1}m, {2}s".format(*time)
    elif len(time) == 2:
        return "{0}m, {1}s".format(*time)
    elif len(time) == 1:
        return "{0}s".format(*time)
    else:
        return ':'.join(str(e) for e in time)


def get_rank(r):
    if r < 1500:
        return 'Bronze'
    elif r < 2000:
        return 'Silver'
    elif r < 2500:
        return 'Gold'
    elif r < 3000:
        return 'Platinum'
    elif r < 3500:
        return 'Diamond'
    elif r < 4000:
        return 'Master'
    elif r < 5000:
        return 'Grandmaster'
    else:
        raise ValueError(f"{r} not a valid rank")


# Returns value associated with user key in replit db. Raises NameError if user not in db
# ValueError if user has no valid data.
def user_index(bnet):
    if bnet in db:
        if not db[bnet][KEYS.TPL]:
            raise ValueError("PRIVATE|DNE")
        return db[bnet]
    else:
        raise NameError


def user_roles(disc):
    if disc not in db:
        print(f"{disc} not in db")
        return None
    bnet = db[disc][KEYS.PRIM]
    try:
        user_data = user_index(bnet)
    except NameError:
        return None
    except ValueError as exc:
        if 'PRIVATE|DNE' in str(exc):
            return None
        raise ValueError
    else:
        # Get user's highest rank
        max_rank = max(user_data[KEYS.RANK].values())
        # Get user's most played hero
        most_played = reduce(lambda r, c: c if user_data[KEYS.TPL][c] > user_data[KEYS.TPL][r] else r, user_data[KEYS.TPL])
        return {'rank-value': str(max_rank), 'rank': get_rank(max_rank), 'most-played': most_played}


def max_key(d):
    mk, mv = None, None
    for k, v in d.items():
        if mk is None or mv is None:
            mk, mv = k, v
        elif v > mv:
            mk, mv = k, v
    return mk


def player_roles(bnet):
    roles = {}
    for mode in db[bnet][KEYS.STAT]:
        roles[mode] = {}
        for categ in db[bnet][KEYS.STAT][mode]:
            hero = next(iter(db[bnet][KEYS.STAT][mode][categ]))
            roles[mode][categ][hero] = db[bnet][KEYS.STAT][mode][categ][hero]
    return roles
