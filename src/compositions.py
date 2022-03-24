from enum import Enum, unique
from typing import Iterable


@unique
class Map(Enum):
    NoMap = ""
    Lijiang = "lijiang-tower"
    Busan = "busan"
    Ilios = "ilios"
    Nepal = "nepal"
    Oasis = "oasis"
    Hanamura = "hanamura"
    Volskaya = "volskaya-industries"
    Anubis = "temple-of-anubis"
    Dorado = "dorado"
    Havana = "havana"
    Junkertown = "junkertown"
    Rialto = "rialto"
    Gibraltar = "watchpoint-gibraltar"
    BlizzardWorld = "blizzard-world"
    Eichenwalde = "eichenwalde"
    Hollywood = "hollywood"
    KingsRow = "kings-row"
    Numbani = "numbani"


@unique
class Round(Enum):
    All = ""
    Offense = "offense"
    Defense = "defense"

    # Lijiang rounds
    Garden = "garden"       # Garden is both a lijiang and oasis round, and is shared by both
    ControlCenter = "control-center"
    NightMarket = "night-market"

    # Busan rounds
    Downtown = "downtown"
    Sanctuary = "sanctuary"
    MekaBase = "meka-base"

    # Ilios rounds
    Well = "well"
    Ruins = "ruins"
    Lighthouse = "lighthouse"

    # Nepal rounds
    Village = "village"
    Sanctum = "sanctum"
    Shrine = "shrine"

    # Oasis rounds
    University = "university"
    CityCenter = "city-center"


def get_map_name(m: str) -> Map:

    # Control maps
    if m.startswith(("lijiang", "lijaing")):
        return Map.Lijiang
    elif m.startswith("busan"):
        return Map.Busan
    elif m.startswith("ilios"):
        return Map.Ilios
    elif m.startswith("nepal"):
        return Map.Nepal
    elif m.startswith("oasis"):
        return Map.Oasis

    # 2CP maps
    elif m.startswith("hanamura"):
        return Map.Hanamura
    elif m.startswith("volskaya"):
        return Map.Volskaya
    elif m.startswith(("temple", "anubis", "aboobis")):
        return Map.Anubis

    # Escort maps
    elif m.startswith("dorado"):
        return Map.Dorado
    elif m.startswith("havana"):
        return Map.Havana
    elif m.startswith("junker"):
        return Map.Junkertown
    elif m.startswith(("rialto", "railto")):
        return Map.Rialto
    elif m.startswith(("gibraltar", "gibralter", "watchpoint")):
        return Map.Gibraltar
    
    # Hybrid maps
    elif m.startswith("bliz"):
        return Map.BlizzardWorld
    elif m.startswith("eich"):
        return Map.Eichenwalde
    elif m.startswith("holly"):
        return Map.Hollywood
    elif m.startswith("king") or m == "kr":
        return Map.KingsRow
    elif m.startswith("numbani"):
        return Map.Numbani
    
    # Return 'none' but in enum form
    else:
        return Map.NoMap


def get_round_name(r: str) -> Round:

    if r in ("offense", "o", "off"):
        return Round.Offense
    elif r in ("defense", "d", "def"):
        return Round.Defense
    
    # Lijiang rounds
    elif r.startswith("control"):
        return Round.ControlCenter
    elif r.startswith("night"):
        return Round.NightMarket
    
    # Lijiang/Oasis round
    elif r.startswith("garden"):
        return Round.Garden
    
    # Busan rounds
    elif r.startswith("downtown"):
        return Round.Downtown
    elif r.startswith(("sanctuary", "sacntuary")):
        return Round.Sanctuary
    elif r.startswith("meka"):
        return Round.MekaBase

    # Ilios rounds
    elif r.startswith("well"):
        return Round.Well
    elif r.startswith("ruins"):
        return Round.Ruins
    elif r.startswith("lighthouse"):
        return Round.Lighthouse

    # Nepal rounds
    elif r.startswith("village"):
        return Round.Village
    elif r.startswith(("sanctum", "sacntum")):
        return Round.Sanctum
    elif r.startswith("shrine"):
        return Round.Shrine

    # Oasis rounds
    elif r.startswith(("university", "univserity")):
        return Round.University
    elif r.startswith("city"):
        return Round.CityCenter
    else:
        return Round.All


def get_map(map_name: str, round_name: str) -> tuple[Map, Round]:
    """Returns map and round name of list of arguments
    """
    ow_map = get_map_name(map_name.lower())
    if ow_map == Map.NoMap:
        return Map.NoMap, Round.ALL
    else:
        return ow_map, get_round_name(round_name.lower())
    