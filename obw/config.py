from pathlib import Path

SRC = Path(__file__).parent
GET = SRC.joinpath("GET")

from platform import system
if system() == "Windows":
    x = "split.exe"
else:
    x = "split"

SPLIT = SRC.joinpath(f"split/{x}")

loud = True
