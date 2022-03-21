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
    comp_name = re.compile(
        "^.*competitive-rank-role-icon[\"].*[\"](.*)[\"].*$"    # Match name of role (tank, damage, support)
    )
    comp_rank = re.compile(
        "^.*competitive-rank-level.*>([0-9]+)"      # Match actual rank, only numbers
    )

    if not ps.stdout:
        raise ValueError(f"Empty result from process: {repr(ps)}")
    elif ps.stdout.find("this profile is currently private") != -1:
        raise PrivateProfileError(profile=(bnet, pf))
    elif ps.stdout.find("profile not found") != -1:
        raise ProfileNotFoundError(url, profile=(bnet, pf))
    else:

        url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

        player_stats = {}
        player_ranks = {}

        lines = ps.stdout.split('\n')
        hero = value = id0x = gamemode = role = rank = ""
        for line in lines:
            if (m := comp_name.match(line)) is not None:
                role = m.groups()[0].split(url_prefix)[1].split('-')[0]
            elif (m := comp_rank.match(line)) is not None and role:
                rank, = m.groups()
                player_ranks[role] = rank
            elif (m := stat_id.match(line)) is not None:
                id0x, = m.groups()
                if id0x.startswith("0x08"):
                    player_stats[gamemode][id0x] = {}
            elif (m := stat_title.match(line)) is not None and id0x.startswith("0x08"):
                hero, = m.groups()
            elif (m := stat_description.match(line)) is not None and id0x.startswith("0x08") and hero:
                value, = m.groups()
                player_stats[gamemode][id0x][hero] = value
            elif (m := stat_gamemode.match(line)) is not None:
                gamemode, = m.groups()
                player_stats[gamemode] = {}
    
    return player_ranks, player_stats
    