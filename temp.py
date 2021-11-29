from replit import db
from remove import remove_bnet, remove_user, is_shared
from add_member import add

def print_db():
  for key in db:
    if key not in ('roles', 'ranks'):
      print("{0}: {1}".format(key, db[key]))

def clear_db():
  db['all_bnet'] = []
  db['all_disc'] = []
  for key in db:
    if '#' in key:
      del db[key]

user1 = 'aarpyy#3360'
bnet1 = 'Aarpyy#1975'
user2 = 'ABGrabbits#4555'
bnet2 = 'Breadnaught#11346'
bnet3 = 'Aaarpyy#1846'

# clear_db()

# add(user1, bnet3)
# add(user2, bnet1)
# add(user1, bnet1)

# print(remove_user(user1))
# print(remove_user(user2))
# print(remove_bnet(user1, bnet1))
# print(remove_bnet(user1, bnet3))
# print(is_shared(bnet1))
# print_db()
