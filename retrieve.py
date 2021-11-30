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
    bnet = db[disc][KEYS.PRM]
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
        max_rank = max(user_data[KEYS.RNK].values())
        # Get user's most played hero
        most_played = reduce(lambda r, c: c if user_data[KEYS.TPL][c] > user_data[KEYS.TPL][r] else r, user_data[KEYS.TPL])
        return {'rank-value': str(max_rank), 'rank': get_rank(max_rank), 'most-played': most_played}


def player_stats(bnet, *, _key=None):
    try:
        user_data = user_index(bnet)

        # Prepare data for easy printing
        ranks = {key.capitalize(): str(value) for key, value in user_data[KEYS.RNK].items()}
        time_played = {key: seconds_to_time(value) for key, value in user_data[KEYS.TPL].items()}
    except NameError:
        # If NameError raised from get_user(), then username does not have linked battlenet
        return 'No Battle.net accounts are linked to your Discord yet!'
    except ValueError:
        return 'Battle.net account is not viewable'
    else:
        message = ""
        if _key == 'rank':
            message += "Your competitive rank(s):\n"
            message += '\n'.join(': '.join(e) for e in ranks.items())
        elif _key == 'time':
            message += "Your top 10 most played heroes:\n"
            message += '\n'.join(': '.join(e) for e in time_played.items())
        else:
            message += "Your player stats:\n"
            message += '\n'.join(': '.join(e) for e in ranks.items())
            message += '\n-----\n'
            message += '\n'.join(': '.join(e) for e in time_played.items())
        return message
