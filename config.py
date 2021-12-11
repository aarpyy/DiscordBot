# Config file for main script request.py
import os


# Class for constant database keys to prevent typos in keys that are not user dependant
class db_key:
    def __init__(self):
        # Indices for...
        self.PRIM = 'primary'           # user's primary battlenet
        self.ALL = 'all'                # dict of all user's battlenets
        self.BNET = 'battlenets'        # list of all battlenets
        self.MMBR = 'members'           # dict of members
        self.STAT = 'user-stats'        # battlenet specific stats
        self.RANK = 'ranks'
        self.ROLE = 'roles'
        self.ADMN = 'admin'
        self.EMJ = 'emoji'
        self.PLTFRM = 'platform'
        self.CATEG = 'data-categories'
        self.BOT = 'bots'
        self.BTRL = 'bot-created-roles'
        self._keys = [self.PRIM, self.ALL, self.BNET, self.MMBR, self.BOT,
                      self.STAT, self.RANK, self.ROLE, self.ADMN, self.EMJ, self.PLTFRM, self.CATEG]

    @property
    def const(self):
        return [self.BNET, self.MMBR, self.RANK, self.ROLE, self.ADMN, self.EMJ, self.CATEG, self.BOT]

    def __contains__(self, item):
        return item in self._keys

    def __iter__(self):
        yield from self._keys


# key object for easy importing
KEYS = db_key()
data_categories = {'Time Played', 'Win Percentage'}


def init():
    # If either executable does not exist (if clean was auto-run) make it
    if not os.path.isfile('split'):
        os.system('make split')
