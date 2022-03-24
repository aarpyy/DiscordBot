from src.config import db, root, path_split, cURL
from src.db_keys import MAP, BNET, MMBR
from unidecode import unidecode
from src.utils import jsondump
import subprocess as sp
import re


def load_data_categories():
    # Open process getting html from playoverwatch.com, pipe output into split command
    cmd = [cURL, "-s", "https://playoverwatch.com/en-us/career/pc/Aarpyy-1975/"]
    ps_cURL = sp.Popen(cmd, stdout=sp.PIPE, text=True, encoding="utf-8")

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
                value, option_id = m.groups()

                # id's that start with 0x are all category id's, but if it starts with 0x02 then its a hero,
                # not general category, so we just want 0x08...
                if value.startswith("0x08"):   
                    categories[value] = unidecode(option_id)
        return categories
    else:
        raise ValueError(f"Subprocess return code: {ps.returncode}")


def load_map_compositions():
    from json import load
    with open(str(root.joinpath("resources/maps.json")), "r") as maps:
        db[MAP] = load(maps)


def dump():
    with open(root.joinpath("resources/userdata.json"), "w") as outfile:
        outfile.write(jsondump(db))


def clear_user_data():
    for key in (BNET, MMBR):
        if key in db:
            del db[key]
        