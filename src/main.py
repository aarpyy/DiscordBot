from os.path import exists, join
from os import system
from sys import platform

gcc_flags = "-g -pedantic -std=c99 -Wall -Wextra"


if __name__ == "__main__":
    for f in ("comp", "dne", "is_private", "stats"):
        if not exists(join("../get", f)):
            exit(1)

    print(platform)
    system(f"gcc {gcc_flags} -o src/split/split src/split/split.c")
