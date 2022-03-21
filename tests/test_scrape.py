from obw.scrape import scrape_play_ow
from obw.obw_errors import PrivateProfileError, ProfileNotFoundError
from sys import stderr
from obw.config import *
from replit import db


def test_scrape(user="Aarpyy#1975"):
    from obw.database import data_categories, map_compositions
    print(data_categories())
    map_compositions()
    
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
    
    for k, v in db.items():
        print(f"{k}: {v}")


def test_all():
    test_scrape()


if __name__ == "__main__":
    test_all()
    