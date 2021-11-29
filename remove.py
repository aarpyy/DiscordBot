from replit import db

def safe_del(obj, key):
  if key in obj:
    del obj[key]

def safe_del_bnet(bnet):
  safe_del(db, bnet)
  if bnet in db['all_bnet']:
    db['all_bnet'].remove(bnet)

def safe_del_disc(user):
  safe_del(db, user)
  if user in db['all_disc']:
    db['all_disc'].remove(user)

def is_shared(bnet):  
  links = 0
  for disc in db['all_disc']:
    if bnet in db[disc]['all']:
      links += 1
  
  return links > 1

def remove_user(user):
  if user in db:
    # Iterate through all user's battletags, removing all that are not shared by another discord user
    for bnet in db[user]['all']:
      if not is_shared(bnet):
        safe_del_bnet(bnet)
    
    # Remove user from list of all discords
    safe_del_disc(user)
    return "{0} successfully removed!".format(user)
  else:
    return "{0} not a registered user".format(user)

# Remove all links between user and specific battletag. If battletag is linked only to this user, also remove its index.
def remove_bnet(user, bnet):  
  if user not in db:
    return "{0} does not have any linked accounts".format(user)
  
  # If battletag is not shared, delete the entry as key and from list of all_bnet
  if not is_shared(bnet):
    safe_del_bnet(bnet)

  # Remove from user's list
  if bnet in db[user]['all']:
    db[user]['all'].remove(bnet)

  # If just removed primary:
  if bnet == db[user]['primary']:
    # If user has another battlenet to become primary, make it primary, otherwise delete user and remove from list of discords
    if db[user]['all']:
      db[user]['primary'] = db[user]['all'][0]
      return "{0} successfully unlinked from {1}. Your new primary battlenet is {2}".format(bnet, user, db[user]['primary'])
    else:
      del db[user]
      db['all_disc'].remove(user)
    
  return "{0} successfully unlinked from {1}".format(bnet, user)

    
  
