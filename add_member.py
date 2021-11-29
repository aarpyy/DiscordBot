import player_request
from remove import remove_bnet
from replit import db

def add_bnet(username, bnet):  
  # Add battlenet tag to list of tags associated with this username
  if username not in db:
    print("adding {0} to database...".format(username))
    db[username] = {'primary': bnet, 'all': [bnet]}
  elif bnet not in db[username]['all']:
    print("adding {0} to {1}'s all...".format(bnet, username))
    db[username]['all'].append(bnet)
  
  # If discord not in list of registered users, add it
  if username not in db['all_disc']:
    db['all_disc'].append(username)

  # If user not listed under loaded battlenets, add it
  if bnet not in db['all_bnet']:
    db['all_bnet'].append(bnet)
  
def add_user(user, bnet):
  # Load bnet information in table
  player_request.main(bnet)
  
  # If player_request was unable to load time played, then this user is either private or DNE
  if not db[bnet]['time-played']:
    # Delete data associated with battletag if it is inaccessible
    remove_bnet(bnet)
    raise ValueError(bnet, "is either private or does not exist")

def add(user, bnet):
  add_bnet(user, bnet)
  add_user(user, bnet)
