from enum import Enum, unique


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


def map_name(args: list[str]) -> tuple[Map, list[str]]:

    s = args[0]

    # Control maps
    if s in ("lijiang-tower", "lijiang", "lijaing"):
        if len(args) > 2 and args[1] == "tower":
            rem = args[2:]
        elif len(args) > 1 and args[1] != "tower":
            rem = args[1:]
        else:
            rem = []
        return Map.Lijiang, rem
    elif s == "busan":
        return Map.Busan, args[1:]
    elif s == "ilios":
        return Map.Ilios, args[1:]
    elif s == "nepal":
        return Map.Nepal, args[1:]
    elif s == "oasis":
        return Map.Oasis, args[1:]

    # 2CP maps
    elif s == "hanamura":
        return Map.Hanamura, args[1:]
    elif s in ("volskaya-industries", "volskaya"):
        if len(args) > 2 and args[1] in ("industries", "industry"):
            rem = args[2:]
        elif len(args) > 1 and args[1] not in ("industries", "industry"):
            rem = args[1:]
        else:
            rem = []
        return Map.Volskaya, rem
    elif s in ("temple-of-anubis", "temple", "anubis", "aboobis"):
        if len(args) > 1:
            args = args[1:]
            while args[0] in ("of", "anubis", "aboobis"):
                args = args[1:]
            rem = args
        else:
            rem = []
        return Map.Anubis, rem

    # Escort maps
    elif s == "dorado":
        return Map.Dorado, args[1:]
    elif s == "havana":
        return Map.Havana, args[1:]
    elif s in ("junker", "junkertown"):
        return Map.Junkertown, args[1:]
    elif s in ("rialto", "railto"):
        return Map.Rialto, args[1:]
    elif s in (
            "watchpoint-gibraltar", "watchpoint-gibralter", "watchpoint",
            "watchpoint:", "gibraltar", "gibralter"
    ):
        if len(args) > 2 and args[1] in ("gibralter", "gibraltar"):
            rem = args[2:]
        elif len(args) > 1 and args[1] not in ("gibralter", "gibraltar"):
            rem = args[1:]
        else:
            rem = []
        return Map.Gibraltar, rem
    
    # Hybrid maps
    elif s in ("blizzard-world", "blizzard", "bliz", "blizz"):
        if len(args) > 2 and args[1] == "world":
            rem = args[2:]
        elif len(args) > 1 and args[1] != "world":
            rem = args[1:]
        else:
            rem = []
        return Map.BlizzardWorld, rem
    elif s in ("eichenwalde", "eich", "eichenwald", "eichanwalde", "eichenvalde"):
        return Map.Eichenwalde, args[1:]
    elif s in ("hollywood", "holly"):
        return Map.Hollywood, args[1:]
    elif s in ("kings-row", "kings", "king's", "kr"):
        if len(args) > 2 and args[1]  == "row":
            rem = args[2:]
        elif len(args) > 1 and args[1] != "row":
            rem = args[1:]
        else:
            rem = []
        return Map.KingsRow, rem
    elif s == "numbani":
        return Map.Numbani, args[1:]
    
    # Return 'none' but in enum form
    else:
        return Map.NoMap, []


def round_name(args: list[str]) -> Round:

    s = args[0]
    if s in ("offense", "o", "off"):
        return Round.Offense
    elif s in ("defense", "d", "def"):
        return Round.Defense
    
    # Lijiang rounds
    elif s in ("control", "control-center", "controlcenter"):
        return Round.ControlCenter
    elif s in ("night", "market", "night-market", "nightmarket"):
        return Round.NightMarket
    
    # Lijiang/Oasis round
    elif s in ("garden", "gardens"):
        return Round.Garden
    
    # Busan rounds
    elif s == "downtown":
        return Round.Downtown
    elif s in ("sanctuary", "sacntuary"):
        return Round.Sanctuary
    elif s in ("meka", "mekabase", "meka-base"):
        return Round.MekaBase

    # Ilios rounds
    elif s == "well":
        return Round.Well
    elif s == "ruins":
        return Round.Ruins
    elif s == "lighthouse":
        return Round.Lighthouse

    # Nepal rounds
    elif s == "village":
        return Round.Village
    elif s in ("sanctum", "sacntum"):
        return Round.Sanctum
    elif s == "shrine":
        return Round.Shrine

    # Oasis rounds
    elif s in ("university", "univserity"):
        return Round.University
    elif s in ("city", "center", "city-center", "citycenter"):
        return Round.CityCenter
    else:
        return Round.All


def path_get_map(args: list[str]) -> tuple[Map, Round]:
    """Returns map and round name of list of arguments

    :param args: command arguments
    :type args: list[str]
    :return: map and round name
    :rtype: tuple[Map, Round]
    """
    ow_map, args = map_name([a.lower() for a in args])
    if ow_map == Map.NoMap:
        return Map.NoMap, Round.All
    elif len(args) == 0:
        return ow_map, Round.All
    else:
        return ow_map, round_name(args)
    