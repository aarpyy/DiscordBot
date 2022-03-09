from src.db import *
from tools import jsondump


outfile = "../temp/out.json"


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
