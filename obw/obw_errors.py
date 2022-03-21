class PrivateProfileError(Exception):

    def __init__(self, message="", *, profile=None):
        super().__init__(message)
        self._profile = profile

    @property
    def profile(self):
        return self._profile


class ProfileNotFoundError(Exception):

    def __init__(self, message="", *, profile=None):
        super().__init__(message)
        self._profile = profile

    @property
    def profile(self):
        return self._profile
