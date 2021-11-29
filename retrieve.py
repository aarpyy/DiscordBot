from replit import db

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
    return ':'.join(time)

# Returns value associated with user key in replit db. Raises NameError if user not in db, ValueError is user has no valid data.
def get_user(bnet):
  if bnet in db:
    if not db[bnet]['time-played']:
      raise ValueError from None
    return db[bnet]
  else:
    raise NameError from None

def get_roles(disc):
  if disc not in db:
    return None
  bnet = db[disc]['primary']
  try:
    user_data = get_user(bnet)
  except NameError:
    return None
  except ValueError:
    return None
  else:
    max_rank = max(user_data['ranks'].values())
    return {max_rank, user_data['time-played'].keys()[0]}

def get_data(bnet, *, key=None):
  try:
    user_data = get_user(bnet)

    # Prepare data for easy printing
    ranks = {key.capitalize(): str(value) for key, value in user_data['ranks'].items()}
    time_played = {key: seconds_to_time(value) for key, value in user_data['time-played'].items()}
  except NameError:
    # If NameError raised from get_user(), then username does not have linked battlenet
    return 'No Battle.net accounts are linked to your Discord yet!'
  except ValueError:
    return 'None of the account(s) linked to your Discord are viewable'
  else:
    message = ""
    if key == 'rank':
      message += "Your competitive rank(s):\n"
      message += '\n'.join(': '.join(e) for e in ranks.items())
    elif key == 'time':
      message += "Your top 10 most played heroes:\n"
      message += '\n'.join(': '.join(e) for e in time_played.items())
    else:
      message += "Your player stats:\n"
      message += '\n'.join(': '.join(e) for e in ranks.items())
      message += '\n-----\n'
      message += '\n'.join(': '.join(e) for e in time_played.items())
    return message
