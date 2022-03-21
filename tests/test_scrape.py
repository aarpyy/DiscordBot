from obw.scrape import scrape_play_ow
from obw.obw_errors import PrivateProfileError, ProfileNotFoundError
from sys import stderr


def test_scrape(user="Aarpyy#1975"):
    try:
        _, st = scrape_play_ow(user)
    except PrivateProfileError as exc:
        print(f"{exc.profile} is private", file=stderr)
    except ProfileNotFoundError:
        assert False
    except ValueError as exc:
        raise ValueError(f"{test_scrape.__name__} failed") from exc
    else:
        assert bool(st)


def test_all():
    test_scrape()


if __name__ == "__main__":
    test_all()
    