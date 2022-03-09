from os.path import exists, join, pardir
from os import chdir, getcwd, system
from sys import platform, stderr

import os

from pathlib import Path

__dir__ = Path(__file__).parent.absolute()

GET = __dir__.joinpath("GET")

print(GET)

split = "split."

for fname in ("comp", "dne", "is_private", "stats"):
    if not GET.joinpath(fname).exists():
        print(f"{fname} does not exist", file=stderr)
        exit(1)

if platform.startswith("darwin"):
    split += "macos"
else:
    split += "linux"


if not GET.joinpath(f"{str(GET)}/{split}").exists():
    curr = getcwd()
    chdir(str(GET.joinpath("split")))
    system("make")
    chdir(curr)

config = {
    "__dir__": __dir__,
    "GET": GET,
    "split": split
}
