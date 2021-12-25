from replit import db

from config import KEYS
from tools import getkey

from typing import Union


def battlenet(bnet: str, disc: str) -> Union[str, int]:
    """
    Removes battlenet from replit database, returning flag of if the user's primary
    account was removed.
    :param bnet: battlenet to be removed
    :param disc: discord user associated with battlenet
    :return: new primary iff account removed was user's old primary, 0 otherwise
    """
    db[KEYS.BNET].remove(bnet)                          # Remove from list of all battlenets

    if db[KEYS.MMBR][disc][bnet][KEYS.PRIM]:            # If it was this user's primary account,
        del db[KEYS.MMBR][disc][bnet]                   # first remove it then,
        if db[KEYS.MMBR][disc]:                         # check if they have any other accounts
            new_prim = getkey(db[KEYS.MMBR][disc])      # If they do, make it primary, otherwise do nothing
            db[KEYS.MMBR][disc][new_prim][KEYS.PRIM] = True
            return new_prim
    else:
        del db[KEYS.MMBR][disc][bnet]                   # If it wasn't primary, no problem just removing it

    return 0
