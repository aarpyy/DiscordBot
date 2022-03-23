from pathlib import Path
from os import getenv
from platform import system

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
