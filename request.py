from replit import db

from os import system
from unidecode import unidecode
from collections import deque
import json
from config import KEYS

from typing import Dict, Tuple, Callable


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
    system(f"curl -s {url} | ./split > player.info")

    raise NameError

    try:
        if system("./get/is_private player.info"):
            raise AttributeError("PRIVATE")
        elif system("get/dne player.info"):
            raise NameError("DNE")
        else:
            system("./get/stats player.info > player.stats")
            system("./get/comp player.info > player.comp")
    finally:
        system("rm -f player.info")

    # Python dictionaries for ranks and time played data
    _ranks = {}
    _stats = {}

    lines = deque()
    ranks_found = 0

    with open("player.comp", "r") as infile:
        while line := infile.readline():
            lines.append(line)
            ranks_found += 1
    system("rm -f player.comp")

    url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

    ranks_found //= 4   # Two lines per rank, ranks always appear twice
    for _ in range(ranks_found):
        role_url, _rank = lines.popleft().strip('\n'), lines.popleft().strip('\n')

        # Confirm that role and rank are what is expected
        _role = role_url.split(url_prefix)[1]
        if _role.startswith("https") or not _rank.strip().isnumeric():
            raise ValueError

        # End of url is user specific data, split by / to get end, then split by - to get specific data
        _role = _role.split('-')[0]
        _ranks[_role] = int(_rank)

    lines.clear()

    with open("player.stats", "r") as infile:
        while line := infile.readline():
            lines.append(line)
    system("rm -f player.stats")

    # Get table of data categories
    # with open("categories.json", "r") as infile:
    #     categories = json.load(infile)
    categories = db[KEYS.CTG]

    _stats = {}
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
            _stats[mode] = {}
        elif line.startswith("0x02E"):
            # If its a category type we don't care about, read all the data of that category until we hit
            # either a new mode or a new category, or we finish the file, in which case we return
            while 1:
                line = lines.popleft()
                if not lines:
                    return _ranks, _stats
                elif line.startswith("0x") or line.startswith('|'):
                    lines.appendleft(line)
                    break
        elif line.startswith("0x"):
            categ = categories[line]
            _stats[mode][categ] = {}
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
            elif '%' in stat:
                stat = stat.strip('%')

            _stats[mode][categ][unidecode(line)] = stat

    return _ranks, _stats
