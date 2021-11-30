import os
import unidecode
from config import KEYS
from config import N_HEROES
from replit import db


# Takes in a string in format hr:min:sec and returns the integer value in seconds
def time_to_int(time):
    time = time.split(':')
    total = 0
    while time:
        total = (total * 60) + int(time.pop(0))
    return total


def update(user=None):
    if user is None:
        for player in db[KEYS.BNT]:
            main(player)
        return True
    elif user in db[KEYS.BNT]:
        main(user)
        return True
    else:
        return False


def main(bnet):
    player_name, player_id = bnet.split('#')  # get player name from command line
    url = 'https://playoverwatch.com/en-us/career/pc/{0}-{1}/'.format(player_name, player_id)  # match name to url

    # If either executable does not exist (if clean was auto-run) make it
    if not os.path.isfile('Formatter/split'):
        os.system('cd Formatter; make split')
    if not os.path.isfile('Formatter/format'):
        os.system('cd Formatter; make format')

    # Get html from url in silent mode, split the file by < to make lines easily readable by sed, then
    # run sed command and format output into key/value pairs
    os.system("curl -s {0} | ./Formatter/split | ./getplayerinfo.sh > stdout.txt".format(url))
    # For whatever reason on replit the sed can't pipe stdout to format, so it prints stdout to file
    # that is then read by format
    os.system('./Formatter/format < stdout.txt > temp.txt')
    os.system('rm -f stdout.txt')

    # Python dictionaries for ranks and time played data
    ranks = {}
    time_played = {}

    with open('temp.txt', 'r') as file:
        lines = file.readlines()
        time_data = lines[-N_HEROES:]  # get last 32 lines which are hero usage stats
        comp_data = lines[:-N_HEROES]  # get lines up to last 32 which are comp data

        while comp_data:
            role, rank = comp_data.pop(0), comp_data.pop(0)
            role = role.split('|')[1].split('/')[6].split('-')[1]
            if role not in ranks:
                ranks[role] = int(rank.split('|')[1])

        while time_data:
            hero = time_data.pop(0).split('|')
            # unidecode converts unicode characters to ASCII (ex. ü -> u)
            time_played[unidecode.unidecode(hero[0])] = time_to_int(hero[1].strip('\n'))

    # Remove .rank file to free up space
    os.system('rm -f temp.txt')

    # Update table, regardless of what was there before
    db[bnet] = {KEYS.RNK: ranks, KEYS.TPL: time_played}
