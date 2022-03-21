from replit import db

from os import remove
import subprocess as sp
from unidecode import unidecode
from collections import deque

from typing import Dict, Tuple, Callable

from .db_keys import CTG
from .config import SRC, SPLIT, GET
from .obw_errors import PrivateProfileError, ProfileNotFoundError


temp = SRC.joinpath("temp")
info_file = str(temp.joinpath("player.info"))
comp_file = str(temp.joinpath("player.comp"))
stat_file = str(temp.joinpath("player.stats"))


# Given a platform of overwatch, returns a function that accepts a username of that platform
# and returns a url to that players profile if it exists
def platform_url(platform: str) -> Callable[[str], str]:
    """
    Given a platform (Xbox, PS, or PC) returns the associated PlayOverwatch url for viewing
    career profiles.

    :param platform: name of platform
    :return: function that accepts username and returns url
    """
    if platform.lower() == 'xbox':
        return lambda x: f'https://playoverwatch.com/en-us/career/xbl/{x}/'
    elif platform.lower() == 'playstation':
        return lambda x: f'https://playoverwatch.com/en-us/career/psn/{x}/'
    else:
        return lambda x: f'https://playoverwatch.com/en-us/career/pc/{x.replace("#", "-")}/'


def scrape_play_ow(bnet: str, pf: str = "PC") -> Tuple[Dict, Dict]:
    """
    Requests from playoverwatch.com user data for a given overwatch username, returning
    Python dictionaries containing competitive rank and general statistics. On average
    takes ~5.05s to complete.

    :param bnet: Player's overwatch name
    :param pf: Platform of overwatch account (PC, Xbox, or PS)
    :raises AttributeError: If url requested is for a private battlenet
    :raises NameError: If url requested is for a battlenet that does not exist
    :raises ValueError: If any errors occur reading the data
    :return: dict of ranks, dict of stats
    """

    url = platform_url(pf)(bnet)

    # Get html from url in silent mode, split the file by < to make lines easily readable by sed, then
    # run sed command and format output into key/value pairs
    sp.run(["curl", "-s", url], stdout=sp.PIPE)
    with open(info_file, "w") as infoIO:
        sp.run(str(SPLIT), stdin=sp.PIPE, stdout=infoIO)
    

    # This try block allows for the errors to be raised and player.info removed regardless of
    # errors thrown
    try:
        if sp.run([str(GET.joinpath("is_private")), info_file]).returncode:
            raise PrivateProfileError(profile=(bnet, pf))
        elif sp.run([str(GET.joinpath("dne")), info_file]).returncode:
            raise ProfileNotFoundError(profile=(bnet, pf))
        else:
            with open(stat_file, "w") as statIO:
                sp.run([str(GET.joinpath("stats")), info_file], stdout=statIO)
            with open(comp_file, "w") as compIO:
                sp.run([str(GET.joinpath("comp")), info_file], stdout=compIO)
    finally:
        remove(info_file)

    # Python dictionaries for ranks and time played data
    comp_ranks = {}

    lines = deque()
    ranks_found = 0

    with open(comp_file, "r") as infile:
        while line := infile.readline():
            rnk = line.strip('\n') + "|" + infile.readline().strip('\n')
            if rnk not in lines:
                lines.append(rnk)
                ranks_found += 1
    remove(comp_file)

    url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

    for _ in range(ranks_found):
        role_url, ow_rank = lines.popleft().split("|")

        # Confirm that role and rank are what is expected
        ow_role = role_url.split(url_prefix)[1]
        if ow_role.startswith("https") or not ow_rank.strip().isnumeric():
            raise ValueError("User data loaded not recognizable. Overwatch may have changed it's HTML structure!")

        # End of url is user specific data, split by / to get end, then split by - to get specific data
        ow_role = ow_role.split('-')[0]
        comp_ranks[ow_role] = int(ow_rank)

    lines.clear()

    with open(stat_file, "r") as infile:
        while line := infile.readline():
            lines.append(line)
    remove(stat_file)

    categories = db[CTG]

    bnet_stats = {}
    mode, categ = "", ""

    # If first two lines are not a gamemode and a data category then this data can't be used since its in an
    # unexpected format
    if not lines[0].startswith('|') or not lines[1].startswith("0x"):
        raise ValueError("User data loaded not recognizable. Overwatch may have changed it's stats categories")

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
                total = 0
                for unit in stat.split(':'):
                    total = (total * 60) + int(unit)
                stat = total
            elif '.' in stat:
                stat = float(stat)
            elif '%' in stat:
                stat = int(stat.strip('%'))
            elif stat.isnumeric():
                stat = int(stat)

            bnet_stats[mode][categ][unidecode(line)] = stat

    return comp_ranks, bnet_stats
