from pathlib import Path
from os import getenv
from platform import system

root = Path(__file__).parent.parent.absolute()
path_get = root.joinpath("GET")
if system() == "Windows":
    x = "split.exe"
else:
    x = "split"

path_split = root.joinpath(f"split/{x}")
path_temp = root.joinpath("temp")


# If .env not already loaded, then we are not on repl.it, so load .env and then import db
if not getenv("REPLIT_DB_URL"):
    from dotenv import load_dotenv
    load_dotenv(root.joinpath(".env"))
