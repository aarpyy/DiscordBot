from enum import Enum, unique, auto


rank_names = ("Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master", "Grandmaster")


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class Rank(AutoName):

    Bronze = auto()
    Silver = auto()
    Gold = auto()
    Platinum = auto()
    Diamond = auto()
    Master = auto()
    Grandmaster = auto()


def get_rank(r) -> Rank:
    if r < 1500:
        return Rank.Bronze
    elif r < 2000:
        return Rank.Silver
    elif r < 2500:
        return Rank.Gold
    elif r < 3000:
        return Rank.Platinum
    elif r < 3500:
        return Rank.Diamond
    elif r < 4000:
        return Rank.Master
    else:
        return Rank.Grandmaster
