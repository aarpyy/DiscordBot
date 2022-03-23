from pathlib import Path
from os import getenv
from platform import system


def getdb():
    # This is a function instead of just importing and then assigning later because
    # import needs to be delayed until .env has been confirmed loaded
    import replit
    db: replit.Database = replit.db
    return db


root = Path(__file__).parent.parent.absolute()

# Based on OS, set path to split executable, cURL, and gcc
if system() == "Windows":
    sp = "split.exe"
    is_unix = False
    cURL = "C:\\cygwin64\\bin\\curl.exe" 
    gcc = "C:\\cygwin64\\bin\\gcc.exe"
else:
    sp = "split"
    is_unix = True
    cURL = "curl"
    gcc = "gcc"

path_split = root.joinpath(f"split/{sp}")
path_temp = root.joinpath("temp")

# If split executable not already made, make it in the split directory
if not path_split.is_file():
    import subprocess
    subprocess.run([gcc, "-o", root.joinpath("split/split"), root.joinpath("split/split.c")])


# If .env not already loaded, then we are not on repl.it, so load .env and then import db
if not getenv("REPLIT_DB_URL"):
    from dotenv import load_dotenv
    load_dotenv(root.joinpath(".env"))

# This is what everything else should import for db, since its logged in after loading .env
db = getdb()
