from flask import g
from replit import db

from os import remove
import subprocess as sp
from unidecode import unidecode
from collections import deque
import re

from typing import Dict, Tuple, Callable

from .db_keys import CTG
from .config import root, path_split, path_get, path_temp, is_unix
from .obw_errors import PrivateProfileError, ProfileNotFoundError


info_file = str(path_temp.joinpath("player.info"))
comp_file = str(path_temp.joinpath("player.comp"))
stat_file = str(path_temp.joinpath("player.stats"))


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

    # path_get html from url in silent mode, split the file by < to make lines easily readable by sed, then
    # run sed command and format output into key/value pairs
    if is_unix:
        cURL = "curl"
    else:
        cURL = "C:\\cygwin64\\bin\\curl.exe"

    # sp.run(str(cwd.joinpath("split.exe")), stdin=open(str(cwd.joinpath('temp.txt')), "r"), capture_output=True, text=True)
    ps_cURL = sp.Popen([cURL, "-s", url], stdout=sp.PIPE, text=True, encoding="utf-8")
    ps = sp.run(str(path_split), stdin=ps_cURL.stdout, capture_output=True, text=True, encoding="utf-8")
    ps_cURL.terminate()

    stat_title = re.compile(
        (
            "^.*"                       # Everything up until next match
            "ProgressBar-title\">"      # Match progress bar title
            "([^:]+)"                   # Capture title in group 1
            ".*$"                       # Match rest of line (was in original sed command, probably not important)
        )
    )
    stat_description = re.compile(
        (
            "^.*"
            "ProgressBar-description\">"    # Match description tag
            "(.*)$"                         # Group everything after
        )
    )
    stat_id = re.compile(
        "^.*data-category-id=\"(.*)\".*$"   # Match category id tag, grouping everything inside quotes
    )
    stat_gamemode = re.compile(
        "^<div id=\"(.*)\" data-js=\"career-category\" data-mode=\".*\">.*$"    # Match name of category
    )

    # This try block allows for the errors to be raised and player.info removed regardless of
    # errors thrown
    try:
        cmd = []
        if not is_unix:
            cmd.append("bash")

        if ps.stdout.find("this profile is currently private") != -1:
            raise PrivateProfileError(profile=(bnet, pf))
        elif ps.stdout.find("profile not found") != -1:
            raise ProfileNotFoundError(url, profile=(bnet, pf))
        else:

            player_stats = {}

            lines = ps.stdout.split('\n')
            hero = value = id0x = gamemode = ""
            for line in lines:
                if (m := stat_title.match(line)) is not None:
                    hero, = m.groups()
                    # print(f"title match: {m}; {m.groups()}")
                elif (m := stat_description.match(line)) is not None:
                    player_stats[gamemode][id0x][hero] = value
                    value, = m.groups()
                    # print(f"desc match: {m}; {m.groups()}")
                elif (m := stat_id.match(line)) is not None:
                    id0x, = m.groups()
                    if id0x.startswith("0x02"):
                        break
                    player_stats[gamemode][id0x] = {}
                    # print(f"id match: {m}; {m.groups()}")
                elif (m := stat_gamemode.match(line)) is not None:
                    gamemode, = m.groups()
                    player_stats[gamemode] = {}
                    # print(f"categ match: {m}; {m.groups()}")
            print(player_stats)
                
        # cmd = []
        # if not is_unix:
        #     cmd.append("bash")
        # if sp.run(cmd + [str(path_get.joinpath("is_private.sh")), info_file]).returncode:
        #     raise PrivateProfileError(profile=(bnet, pf))
        # elif sp.run(cmd + [str(path_get.joinpath("dne.sh")), info_file]).returncode:
        #     raise ProfileNotFoundError(url, profile=(bnet, pf))
        # else:
        #     with open(stat_file, "w") as statIO:
        #         sp.run(cmd + [str(path_get.joinpath("stats.sh")), info_file], stdout=statIO)
        #     with open(comp_file, "w") as compIO:
        #         sp.run(cmd + [str(path_get.joinpath("comp.sh")), info_file], stdout=compIO)
    finally:
        # remove(info_file)
        exit(1)

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

    url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

    for _ in range(ranks_found):
        role_url, ow_rank = lines.popleft().split("|")

        # Confirm that role and rank are what is expected
        ow_role = role_url.split(url_prefix)[1]
        if ow_role.startswith("https") or not ow_rank.strip().isnumeric():
            raise ValueError("User data loaded not recognizable. Overwatch may have changed it's HTML structure!")

        # End of url is user specific data, split by / to path_get end, then split by - to path_get specific data
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