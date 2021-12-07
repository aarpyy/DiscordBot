import os
from unidecode import unidecode
from config import KEYS
from functools import reduce
from replit import db


def update(bnet=None):
    if bnet is None:
        for _bnet in db[KEYS.BNET]:
            _update(_bnet)
    else:
        _update(bnet)


def _update(bnet):
    try:
        url = search_url(bnet[KEYS.PLTFRM])(bnet)
    except ValueError as exc:
        raise ValueError(str(bnet)) from exc
    else:
        db[bnet][KEYS.RANK], db[bnet][KEYS.STAT] = main(url)


# Given a platform of overwatch, returns a function that accepts a username of that platform
# and returns a url to that players profile if it exists
def search_url(platform):
    if platform.lower() == 'xbox':
        return lambda x: 'https://playoverwatch.com/en-us/career/xbl/{0}/'.format(x)
    elif platform.lower() == 'playstation':
        return lambda x: 'https://playoverwatch.com/en-us/career/psn/{0}/'.format(x)
    else:
        return lambda x: 'https://playoverwatch.com/en-us/career/pc/{0}-{1}/'.format(x.split('#')[0], x.split('#')[1])


def data_categories():
    if not os.system("./get/category > categories"):
        categ_id = {}
        ctg = []
        with open("categories", "r") as infile:
            lines = infile.readlines()

        for line in lines:
            line = line.strip('\n')
            # Only read categories that start with data-id
            if not line.startswith("0x"):
                continue
            else:
                _id, name = line.split('|')
                name = unidecode(name)
                categ_id[_id] = name
                if name not in ctg:
                    ctg.append(name)

        os.system("rm -f categories")
        return categ_id, ctg

    else:
        raise ValueError("An error occurred in either a curl or sed")


def main(url):
    # Get html from url in silent mode, split the file by < to make lines easily readable by sed, then
    # run sed command and format output into key/value pairs
    os.system(f"curl -s {url} | ./split > player.info")
    os.system(f"./get/stats player.info > player.stats")
    os.system(f"./get/comp player.info > player.comp")
    os.system("rm -f player.info")

    # Python dictionaries for ranks and time played data
    _ranks = {}
    _stats = {}

    with open("player.comp", 'r') as infile:
        lines = infile.readlines()
    os.system("rm -f player.comp")

    # If there are ranks to read
    if len(lines) >= 2:
        _role, rank = lines.pop(0).strip('\n'), lines.pop(0).strip('\n')
        ranks_read = 0
        while lines:
            if ranks_read >= 3:     # All ranks usually appear twice, redudancy adds nothing so ignore
                break

            # Confirm that role and rank are what is expected
            if not _role.startswith("https://static.playoverwatch.com/img/pages/career/icon-") or \
                    not rank.strip().isnumeric():
                raise ValueError

            ranks_read += 1
            # End of url is user specific data, split by / to get end, then split by - to get specific data
            _role = _role.split('/')[-1].split('-')
            _role = _role[_role.index('icon') + 1]

            _ranks[_role] = int(rank)
            _role, rank = lines.pop(0), lines.pop(0)

    with open("player.stats", 'r') as infile:
        lines = infile.readlines()
    os.system("rm -f player.stats")

    # Not having ranks to read is fine but not having stats to read means either private or DNE
    if not len(lines):
        raise ValueError

    # Get table of data categories
    categories, _ = data_categories()

    # Mode of play (either qp or comp) should be first line
    _mode = lines.pop(0).strip('\n')

    # Url was parsed so that game modes are bookended by |
    if not _mode.startswith('|') or not _mode.endswith('|'):
        raise ValueError    # If first line isn't mode, we won't be able to get data
    else:
        _mode = _mode[1:-1]   # Otherwise, get mode and use that

    _stats[_mode] = {}
    line = lines.pop(0).strip('\n')
    if not line.startswith('0x'):   # First line after mode should be data category
        raise ValueError
    _categ = categories[line]
    _stats[_mode][_categ] = {}

    while lines:
        line = lines.pop(0).strip('\n')     # Get first line, always strip \n
        if line.startswith('|') and line.endswith('|'):     # If it is a new mode, set the new mode
            _mode = line[1:-1]
            _stats[_mode] = {}
        elif line.startswith('0x'):     # If a data category, set the new category
            _categ = categories[line]
            _stats[_mode][_categ] = {}
        else:   # Otherwise, it is assumed to be name of hero, pop for stat
            stat = lines.pop(0).strip('\n')
            if not any(c.isdigit() for c in stat):  # If there are no numbers then not valid data
                continue

            if ':' in stat:
                stat = reduce(lambda r, c: (r * 60) + int(c), stat.strip('\n').split(':'), 0)
            elif '%' in stat:
                stat = int(stat.strip('%'))
            elif '.' in stat:
                stat = float(stat)
            else:
                stat = int(stat)
            _stats[_mode][_categ][unidecode(line)] = stat

    # Filters stats so that empty dicts aren't returned (these are mostly fake categories anyway)
    for _mode in _stats:
        _stats[_mode] = {k: v for k, v in _stats[_mode].items() if v}

    return _ranks, _stats
