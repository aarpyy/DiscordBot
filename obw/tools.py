from collections.abc import MutableMapping, MutableSequence

from typing import Union


loud = False


def validate_env():
    from os import getenv

    # If .env not already loaded, then we are not on repl.it, so load .env and then import db
    if not getenv("REPLIT_DB_URL"):
        from dotenv import load_dotenv
        load_dotenv(".env")


def loudprint(*args, **kwargs):
    global loud
    if loud:
        print(*args, **kwargs)


def loudinput(*args, **kwargs):
    global loud
    if loud:
        input(*args, **kwargs)


def jsonify(o: object) -> str:
    """
    Attempts to convert object into JSON readable format.

    :param o: object to be converted
    :return: string hopefully recognizable by JSON
    """

    if isinstance(o, bool):
        return str(o).lower()
    elif isinstance(o, (int, float)):
        return str(o)
    else:
        return f'"{str(o)}"'


def jsondump(obj: Union[MutableMapping, MutableSequence], indent: int = 4) -> str:
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
