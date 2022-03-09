from functools import wraps
from warnings import simplefilter

import pytest

from src.db import *
from src.tools import jsondump


outfile = "../temp/out.json"


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @wraps(func)
    def new_func(ctx, *args):
        if ctx.author
        return func(ctx, *args)

    return new_func


def write_db():
    json_str = jsondump(db)

    with open(outfile, "w") as file:
        file.write(json_str)


def test_init():
    init_db()
    write_db()


def test_add_guild():
    create_guild_index("Oberwatch")
    write_db()


if __name__ == "__main__":
    test_init()

    _all_ = [test_add_guild]

    for test in _all_:
        y = input(f"{test.__name__} (y/n)? ")
        if y.lower() in ("y", "yes"):
            test()
