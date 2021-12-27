from replit import db

from os import system, remove
from unidecode import unidecode
from collections import deque
from config import KEYS

from typing import Dict, Tuple, Callable


info_file = "player.info"
comp_file = "player.comp"
stat_file = "player.stats"


# Given a platform of overwatch, returns a function that accepts a username of that platform
# and returns a url to that players profile if it exists
def search_url(platform: str) -> Callable[[str], str]:
    """
    Given a platform (Xbox, PS, or PC) returns the associated PlayOverwatch url for viewing
    career profiles.

    :param platform: name of platform
    :return: function that accepts username and returns url
    """
    if platform.lower() == 'xbox':
        return lambda x: 'https://playoverwatch.com/en-us/career/xbl/{0}/'.format(x)
    elif platform.lower() == 'playstation':
        return lambda x: 'https://playoverwatch.com/en-us/career/psn/{0}/'.format(x)
    else:
        return lambda x: 'https://playoverwatch.com/en-us/career/pc/{0}/'.format(x.replace('#', '-'))


def main(url: str) -> Tuple[Dict, Dict]:
    """
    Requests from playoverwatch.com user data for a given overwatch username, returning
    Python dictionaries containing competitive rank and general statistics. On average
    takes ~5.05s to complete.

    :param url: url to request from
    :raises AttributeError: If url requested is for a private battlenet
    :raises NameError: If url requested is for a battlenet that does not exist
    :raises ValueError: If any errors occur reading the data
    :return: dict of ranks, dict of stats
    """
    # Get html from url in silent mode, split the file by < to make lines easily readable by sed, then
    # run sed command and format output into key/value pairs
    system(f"curl -s {url} | ./split > {info_file}")
    raise NameError

    # This try block allows for the errors to be raised and player.info removed regardless of
    # errors thrown
    try:
        if system(f"./get/is_private {info_file}"):
            raise AttributeError("PRIVATE")
        elif system(f"./get/dne {info_file}"):
            raise NameError("DNE")
        else:
            system(f"./get/stats {info_file} > {stat_file}")
            system(f"./get/comp {info_file} > {comp_file}")
    finally:
        remove(info_file)

    # Python dictionaries for ranks and time played data
    comp_ranks = {}
    bnet_stats = {}

    lines = deque()
    ranks_found = 0

    with open(comp_file, "r") as infile:
        while line := infile.readline():
            lines.append(line)
            ranks_found += 1
    remove(comp_file)

    url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

    ranks_found //= 4   # Two lines per rank, ranks always appear twice
    for _ in range(ranks_found):
        role_url, ow_rank = lines.popleft().strip('\n'), lines.popleft().strip('\n')

        # Confirm that role and rank are what is expected
        ow_role = role_url.split(url_prefix)[1]
        if ow_role.startswith("https") or not ow_rank.strip().isnumeric():
            raise ValueError

        # End of url is user specific data, split by / to get end, then split by - to get specific data
        ow_role = ow_role.split('-')[0]
        comp_ranks[ow_role] = int(ow_rank)

    lines.clear()

    with open(stat_file, "r") as infile:
        while line := infile.readline():
            lines.append(line)
    remove(stat_file)

    categories = db[KEYS.CTG]

    bnet_stats = {}
    mode, categ = "", ""
    short = {0: 'hrs', 1: 'mins', 2: 'secs'}

    # If first two lines are not a gamemode and a data category then this data can't be used since its in an
    # unexpected format
    if not lines[0].startswith('|') or not lines[1].startswith("0x"):
        raise ValueError

    while lines:
        line = lines.popleft().strip('\n')
        if line.startswith('|'):
            # If its name of mode, set current mode to new mode
            mode = line.strip('|')
            bnet_stats[mode] = {}
        elif line.startswith("0x02E"):
            # If its a category type we don't care about, read all the data of that category until we hit
            # either a new mode or a new category, or we finish the file, in which case we return
            while 1:
                line = lines.popleft()
                if not lines:
                    return comp_ranks, bnet_stats
                elif line.startswith("0x") or line.startswith('|'):
                    lines.appendleft(line)
                    break
        elif line.startswith("0x"):
            categ = categories[line]
            bnet_stats[mode][categ] = {}
        else:
            stat = lines.popleft().strip('\n')
            # All time stats are given hrs:mins:secs even if most significant value is days so we can
            # convert time to integer using integer conversion
            if ':' in stat:
                time_split = stat.split(':')
                for i in range(len(time_split)):
                    j = int(time_split[i])
                    if j:
                        if i in short:
                            stat = f"{j} {short[i]}"
                        break

            bnet_stats[mode][categ][unidecode(line)] = stat

    return comp_ranks, bnet_stats
