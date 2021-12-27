from collections.abc import MutableMapping, MutableSequence

from typing import Union


def getkey(d: dict) -> str:
    """
    Gives first key of dictionary in order of iteration.

    :param d: dictionary
    :return: dictionary key
    """
    return next(iter(d))


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
