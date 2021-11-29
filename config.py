# Config file for main script request.py

N_HEROES = 10


class db_key:
    def __init__(self):
        self.PRM = 'primary'
        self.ALL = 'all'
        self.BNT = 'all_bnet'
        self.DSC = 'all_disc'
        self.TPL = 'time-played'
        self.RNK = 'ranks'
        self.RLE = 'roles'
        self.ADM = 'admin'
        self.EMJ = 'emoji'
        self._keys = [self.PRM, self.ALL, self.BNT, self.DSC, self.TPL, self.RNK, self.RLE, self.ADM, self.EMJ]

    @property
    def const(self):
        return [self.BNT, self.DSC, self.RNK, self.RLE, self.ADM, self.EMJ]

    def __contains__(self, item):
        return item in self._keys

    def __iter__(self):
        yield from self._keys


KEYS = db_key()
