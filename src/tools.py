from collections.abc import MutableMapping, MutableSequence


def jsonify(o):
    """
    Attempts to convert object into JSON readable format.

    :param o: object to be converted
    :return: JSON acceptable data type
    """

    if isinstance(o, bool):

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
