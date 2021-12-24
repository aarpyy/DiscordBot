# Temp functions

def get_key(d: dict):
    return next(iter(d))


def roles(db, disc, bnet):
    roles = set()  # Empty set for roles
    table = db['members'][disc][bnet]['stats']  # Table of battlenet's statistics

    mode_short = {'quickplay': 'qp', 'competitive': 'comp'}

    # For each stat associated with battlenet, add that stat if it is an important one
    for mode in table:
        for rle in table[mode]:
            # Heroes organized in descending stat value already so getting first hero for both of these
            # gets the hero with the best stats
            if rle == 'Win Percentage':
                hero = get_key(table[mode][rle])
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]}W [{mode}]")
            elif rle == 'Time Played':
                hero = get_key(table[mode][rle])
                if mode in mode_short:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode_short[mode]}]")
                else:
                    roles.add(f"{hero}–{table[mode][rle][hero]} [{mode}]")

    table = db['members'][disc][bnet]['rank']

    for rle in table:  # type: str
        roles.add(f"{rle.capitalize()}-{table[rle]}")

    db['members'][disc][bnet]['roles'] = list(roles)
    print("Roles:")
    print(db['members'][disc][bnet]['roles'])


if __name__ == "__main__":
    from os.path import exists
    private = "Sonder#11587"
    public1 = "Dragongale#1783"
    public2 = "Aarpyy#1975"
    dne = "Aarpyyy#1975"

    current = public2
    ranks, stats = main(search_url('PC')(current))
    if exists("example.json"):
        with open("example.json", "r") as infile:
            example = json.load(infile)
    else:
        example = {'members': {"aarpyy#3360": {}}, 'roles': {}, 'battlenets': []}

    example['members']["aarpyy#3360"][current] = {'primary': True, 'rank': ranks, 'stats': stats, 'roles': []}
    example['battlenets'].append(current)

    roles(example, "aarpyy#3360", "Aarpyy#1975")

    with open(f"example.json", "w") as outfile:
        outfile.write(json.dumps(example, indent=4))
