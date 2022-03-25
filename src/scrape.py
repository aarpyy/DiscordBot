import subprocess as sp
import re

from typing import Dict, Tuple, Callable

from .config import path_split, cURL
from .utils import PrivateProfileError, ProfileNotFoundError


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
    Python dictionaries containing competitive rank and general statistics. 
    
    On average takes ~3.5s to complete (On Windows 10, 5600x, 16gb ram)

    :param bnet: Player's overwatch name
    :param pf: Platform of overwatch account (PC, Xbox, or PS)
    :raises PrivateProfileError: If url requested is for a private battlenet
    :raises ProfileNotFoundError: If url requested is for a battlenet that does not exist
    :raises ValueError: If any errors occur reading the data
    :return: dict of ranks, dict of stats
    """

    url = platform_url(pf)(bnet)

    # Open process calling cURL on player's playoverwatch profile
    ps_cURL = sp.Popen([cURL, "-s", url], stdout=sp.PIPE, text=True, encoding="utf-8")

    # Run process splitting html by '<' on output of cURL
    ps = sp.run(str(path_split), stdin=ps_cURL.stdout, capture_output=True, text=True, encoding="utf-8")
    ps_cURL.terminate()     # Terminate cURL process

    if not ps.stdout:
        raise ValueError(f"Empty result from process: {repr(ps)}")
    elif ps.stdout.find("this profile is currently private") != -1:
        raise PrivateProfileError(profile=(bnet, pf))
    elif ps.stdout.find("profile not found") != -1:
        raise ProfileNotFoundError(url, profile=(bnet, pf))
    else:
        stat_title = re.compile((
            "^.*"                           # Everything up until next match
            "ProgressBar-title\">"          # Match progress bar title
            "([^:]+)"                       # Capture title in group 1
            ".*$"                           # Match rest of line (was in original sed command, probably not important)
        ))
        stat_description = re.compile((
            "^.*"
            "ProgressBar-description\">"    # Match description tag
            "(.*)$"                         # Group everything after
        ))
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

        # Url for role icon - from this we can get what role (tank, dmg, supp) the given rank is
        url_prefix = "https://static.playoverwatch.com/img/pages/career/icon-"

        player_stats = {}
        player_ranks = {}

        lines = ps.stdout.split('\n')
        hero = id0x = gamemode = role = ""
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
            elif (m := stat_gamemode.match(line)) is not None:
                gamemode, = m.groups()
                player_stats[gamemode] = {}
            
            # Only work with hero/value if id is valid
            elif (m := stat_title.match(line)) is not None and id0x.startswith("0x08"):
                hero, = m.groups()
            elif (m := stat_description.match(line)) is not None and id0x.startswith("0x08") and hero:
                value, = m.groups()
                player_stats[gamemode][id0x][hero] = value
    
    return player_ranks, player_stats
    