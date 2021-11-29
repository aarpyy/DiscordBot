import json


def update(username, new_dflt):
  with open('battlenet.json', 'r') as infile:
    battletags = json.load(infile)
  
  # If the new default username hasn't been loaded (either because the specific username hasn't linked any battletags or because that specific battletag hasn't been linked) then raise error
  if username not in battletags or new_dflt not in battletags[username]:
    raise KeyError('{0} not linked to {1}'.format(new_dflt, username))
  
  # If no error has been raised, load file and swap out username
  with open('battlenet_default.json', 'r') as infile:
    defaults = json.load(infile)
  
  defaults[username] = new_dflt

  with open('battlenet_default.json', 'w') as outfile:
    outfile.write(json.dumps(defaults, indent=4))
