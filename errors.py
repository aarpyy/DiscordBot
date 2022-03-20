class PrivateProfileError(Exception):

    __slots__ = "_profile"

    def __init__(self, message="", *, profile=None):
        super(message)
        self._profile = profile

    @property
    def profile(self):
        return self._profile


class ProfileNotFoundError(Exception):

    __slots__ = "_profile"

    def __init__(self, message="", *, profile=None):
        super(message)
        self._profile = profile

    @property
    def profile(self):
        return self._profile
