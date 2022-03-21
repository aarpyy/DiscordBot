from replit import db
from .db_keys import MAP
from unidecode import unidecode
from .tools import jsondump
from .config import root, path_split, is_unix
import subprocess as sp
import re


def data_categories():
    # Open process, sending output of category.sh to pipe
    if is_unix:
        cURL = "curl"
    else:
        cURL = "C:\\cygwin64\\bin\\curl.exe"

    # Open process getting html from playoverwatch.com, pipe output into split command
    ps_cURL = sp.Popen([cURL, "-s", "https://playoverwatch.com/en-us/career/pc/Aarpyy-1975/"], stdout=sp.PIPE, text=True, encoding="utf-8")

    # Capture output from split command
    ps = sp.run(str(path_split), stdin=ps_cURL.stdout, capture_output=True, text=True, encoding="utf-8")

    # Now that we've read the result of cURL, we are done with that process
    ps_cURL.terminate()

    # If no error and output was successfully captured
    if not ps.returncode and ps.stdout is not None:
        ctg_regex = re.compile(
            "<option value=[\"](.*)[\"] option-id=[\"](.*)[\"]>.*$"     # Group both name and id
        )
        categories = {}
        lines = ps.stdout.split('\n')
        for line in lines:
            if (m := ctg_regex.match(line)) is not None:
                ID, NAME = m.groups()

                # id's that start with 0x are all category id's, but if it starts with 0x02 then its a hero, not general category, so we just want 0x08...
                if ID.startswith("0x08"):   
                    categories[ID] = unidecode(NAME)
        return categories
    else:
        raise ValueError(f"Subprocess error code: {ps.returncode}")


def map_compositions():
    if db is not None:
        from json import load
        with open(str(root.joinpath("resources/maps.json")), "r") as maps:
            db[MAP] = load(maps)


def dump():
    if db is not None:
        with open("userdata.json", "w") as outfile:
            outfile.write(jsondump(db))
