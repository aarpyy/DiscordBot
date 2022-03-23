from replit import db
from .db_keys import *
from .scrape import platform_url, scrape_play_ow
from .obw_errors import ProfileNotFoundError, PrivateProfileError


# Accessors
def is_active(bnet):
    return db[BNET][bnet][ACTIVE]


def is_hidden(bnet):
    return db[BNET][bnet][HID]


def is_primary(disc, bnet):
    return bnet == db[MMBR][disc][PRIM]


def is_private(bnet):
    return db[BNET][bnet][PRIV]


def get_top(superlative):
    return max(db[MMBR], key=lambda x: db[MMBR][x][SCORE].get(superlative, 0))


def hide(bnet):
    db[BNET][bnet][HID] = True


def deactivate(bnet):
    # Just used for deactivating account so that update roles removes roles, all active accounts are pending removal
    db[BNET][bnet][ACTIVE] = True


# Battlenet methods


def create_index(bnet, pf):
    try:
        rank, stats = scrape_play_ow(platform_url(pf)(bnet))
    except PrivateProfileError:
        db[BNET][bnet] = {
            PRIV: True, ACTIVE: True, HID: False,
            PTFM: pf, RANK: {}, STAT: {}, ROLE: []
        }
        return True
    except ProfileNotFoundError:
        return False
    else:
        db[BNET][bnet] = {
            ACTIVE: True, PRIV: False, HID: False,
            PTFM: pf, RANK: rank, STAT: stats, ROLE: []
        }
        return True


def add(disc, bnet, pf):
    """
    Adds battlenet as index to user object with battlenet data as indices in battlenet object.

    :param disc: name of discord user
    :param bnet: name of battlenet
    :param pf: platform of battlenet
    :return: if battlenet was added to user
    """
    if create_index(bnet, pf):
        db[MMBR][disc][BNET].append(bnet)
        if db[MMBR][disc][PRIM] is None:
            db[MMBR][disc][PRIM] = bnet
        return True
    else:
        return False


def update(bnet):
    """
    Requests data for battlenet, updating its stats and rank if request was successful. If account is private,
    it is marked as such and data is set to empty. If account DNE or is inaccessible, it is set to inactive
    to be deleted.

    :param bnet: battlenet
    :return: None
    """
    ranks, stats = {}, {}
    try:
        # Try to scrape, 
        ranks, stats = scrape_play_ow(bnet, db[BNET][bnet][PTFM])
    except PrivateProfileError:

        # If marked as private, still add the index, but set it to private
        db[BNET][bnet][PRIV] = True
        print(f"{bnet} marked as private")
    except ProfileNotFoundError as exc:

        # If not found, just remove it
        print(f"{exc.profile} not found on playoverwatch.com")
        remove(bnet)
    except ValueError:
        db[BNET][bnet][ACTIVE] = False
        print(f"{bnet} marked as inactive")
    else:
        # If no error raised, then profile not private
        db[BNET][bnet][PRIV] = False
    finally:
        db[BNET][bnet][STAT] = stats
        db[BNET][bnet][RANK] = ranks


def remove(bnet, gld="", disc=""):
    """
    Removes battlenet from table of battlenets as well as all users
    in database, unless guild and user are provided, in which case it just removes
    from that index.

    :param bnet: battlenet to be removed
    :param gld: guild that user belongs to
    :param disc: discord user associated with battlenet
    :return: None
    """

    def remove_from_user(g, d, b):
        db[MMBR][d][BNET].remove(b)
        if bnet == db[MMBR][d][PRIM]:
            if db[MMBR][d][BNET]:
                db[MMBR][d][PRIM] = db[MMBR][d][BNET][0]
            else:
                db[MMBR][d][PRIM] = None

    # TODO: Remove user roles (maybe?)

    if bnet in db[BNET]:
        del db[BNET][bnet]  # Remove battlenet from database

    # If guild and discord provided, remove directly
    if disc and gld:
        remove_from_user(gld, disc, bnet)

    # Otherwise, just search through all guilds and users, removing from everyone
    else:
        for gld in db[GLD]:
            for disc in db[MMBR]:
                if bnet in db[MMBR][disc][BNET]:

                    # Technically battlenets are unique to a user, but it doesn't really hurt to
                    # search through all after finding one since removing rarely happens and on
                    # the off chance a bug allowed for a bnet to be shared it will now be removed
                    remove_from_user(gld, disc, bnet)
