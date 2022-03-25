from collections.abc import MutableMapping, MutableSequence
from functools import wraps
from discord.commands import ApplicationContext
from sys import stderr


su = "aarpyy#3360"


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


def restrict(users=None):
    """Given a list of users, returns a wrapper that restricts
    the use of a discord command except for the given users.

    :param users: List of users with permission to use function, defaults to super user (aarpyy)
    :type users: list[str], optional
    :return: wrapper, restricting bot.command()
    :rtype: function
    """
    if users is None:
        global su
        users = [su]

    def decorator(f):

        global su

        @wraps(f)
        async def restricted(*args, **kwargs):

            # Find the context arg, either first or second depending on if procedure or class method
            ctx = None
            for a in args:
                if isinstance(a, ApplicationContext):
                    ctx = a
                    break

            if ctx is None or str(ctx.author) in users:
                await f(*args, **kwargs)
            else:
                print(f"{str(ctx.author)} ran {f.__name__} and was blocked.", file=stderr)
                await ctx.respond(f"This command is currently disabled!")

        return restricted

    return decorator


def jsonify(o):
    """
    Attempts to convert object into JSON readable format.

    :param o: object to be converted
    :return: JSON acceptable data type
    """

    if o is None:
        return "null"
    elif isinstance(o, bool):

        # JSON booleans are lowercase
        return str(o).lower()
    elif isinstance(o, (int, float)):

        # JSON recognizes ints and floats
        return str(o)
    else:

        # Otherwise just wrap it in quotes since JSON can handle normal strings
        return f'"{str(o)}"'


def jsondump(obj, indent=4):
    """
    Converts a MutableMapping or MutableSequence object into a JSON string.

    :param obj: MutableMapping|MutableSequence object
    :param indent: number of spaces per standard indent
    :return: JSON string
    """

    # Recursive dump function that converts each instance into a JSON object, and each of its elements
    # recursively into JSON objects
    def dumpitem(o, i):
        if isinstance(o, MutableMapping):
            s = "{"
            prefix = " " * i
            s += ",".join(f"\n{prefix}{jsonify(k)}: {dumpitem(v, i + indent)}" for k, v in o.items())
            if o:
                s += "\n" + " " * (i - indent)
            return s + "}"
        elif isinstance(o, MutableSequence):
            s = "["
            prefix = " " * i
            s += ",".join(f"\n{prefix}{jsonify(e)}" for e in o)
            if o:
                s += "\n" + " " * (i - indent)
            return s + "]"
        else:
            return jsonify(o)

    return dumpitem(obj, indent)
