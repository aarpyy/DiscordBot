from replit import db
from .db_keys import MAP
from unidecode import unidecode
from .tools import jsondump
from .config import path_get, root, path_split, is_unix
import subprocess as sp


def data_categories():
    # Open process, sending output of category.sh to pipe
    cmd = []
    if not is_unix:
        cmd.append("bash")
    cmd.extend([str(path_get.joinpath("category.sh")), str(path_split)])
    cp = sp.Popen(cmd, stdout=sp.PIPE)

    # If successful and bytes were read, then read them in as lines
    if not cp.returncode and cp.stdout is not None:
        categories = {}
        lines = list(cp.stdout.readlines())
        # print(lines)
        for line in lines:
            line = line.decode().strip('\n')    # Convert to string with utf-8 (default)

            # Only read categories that start with data-id
            if line.startswith("0x"):
                _id, name = line.split('|')
                name = unidecode(name)
                categories[_id] = name
        cp.terminate()
        return categories
    else:
        cp.terminate()
        raise ValueError(f"Subprocess error code: {cp.returncode}")


def map_compositions():
    if db is not None:
        from json import load
        with open(str(root.joinpath("resources/maps.json")), "r") as maps:
            db[MAP] = load(maps)


def dump():
    if db is not None:
        with open("userdata.json", "w") as outfile:
            outfile.write(jsondump(db))
