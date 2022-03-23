from src.config import *
from src.scrape import scrape_play_ow
from src.obw_errors import PrivateProfileError, ProfileNotFoundError
from sys import stderr
from src.config import db


def test_scrape(user="Aarpyy#1975"):
    from src.database import load_data_categories, load_map_compositions
    load_data_categories()
    load_map_compositions()
    
    assert db is not None

    try:
        _, st = scrape_play_ow(user)
    except PrivateProfileError as exc:
        print(f"{exc.profile} is private", file=stderr)
    except ProfileNotFoundError as exc:
        print(str(exc))
        assert False
    except ValueError as exc:
        raise ValueError(f"{test_scrape.__name__} failed") from exc
    else:
        assert bool(st)


def test_scrape_average(user="Aarpyy#1975"):
    from timeit import timeit
    i = 5
    t = timeit(lambda: scrape_play_ow(user), number=i)
    print(f"Average scrape time: {t / i :.2f}s")
    