from replit import db
from config import *
from functools import reduce


# Converts time (in seconds) to list of time intervals in descending magnitudes of time
def sec_to_t(t):
    time = []
    while t:
        t, r = divmod(t, 60)
        time.append(r)
    return time[::-1]


def get_rank(r):
    if r < 1500:
        return 'bronze'
    elif r < 2000:
        return 'silver'
    elif r < 2500:
        return 'gold'
    elif r < 3000:
        return 'platinum'
    elif r < 3500:
        return 'diamond'
    elif r < 4000:
        return 'master'
    elif r < 5000:
        return 'grandmaster'
    else:
        raise ValueError("{0} not a valid rank".format(r))


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
        return ':'.join(time)


# Returns value associated with user key in replit db. Raises NameError if user not in db
# ValueError if user has no valid data.
def get_user(bnet):
    if bnet in db:
        if not db[bnet][key_t]:
            raise ValueError
        return db[bnet]
    else:
        raise NameError


def get_roles(disc):
    if disc not in db:
        return None
    bnet = db[disc][key_pr]
    try:
        user_data = get_user(bnet)
    except NameError:
        return None
    except ValueError:
        return None
    else:
        # Get user's highest rank
        max_rank = get_rank(max(user_data[key_r].values()))
        # Get user's most played hero
        most_played = reduce(lambda r, c: c if user_data[key_t][c] > user_data[key_t][r] else r, user_data[key_t])
        return {max_rank, most_played}


def get_data(bnet, *, _key=None):
    try:
        user_data = get_user(bnet)

        # Prepare data for easy printing
        ranks = {key.capitalize(): str(value) for key, value in user_data[key_r].items()}
        time_played = {key: seconds_to_time(value) for key, value in user_data[key_t].items()}
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
