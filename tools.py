from collections.abc import MutableMapping, MutableSequence


def getkey(d):
    return next(iter(d))


def jsonify(o):
    if isinstance(o, str):
        return f'"{o}"'
    elif isinstance(o, bool):
        return str(o).lower()
    else:
        return str(o)


def jsondump(obj, indent=4):

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
