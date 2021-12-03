import json


def load():
    with open("table.json", "r") as infile:
        return json.load(infile)


def update(table):
    with open("table.json", "w") as outfile:
        outfile.write(json.dumps(table, indent=4))


class Table:

    def __init__(self):
        self.table = {}
        update({})

    def __contains__(self, item):
        self.table = load()
        return item in self.table

    def __getitem__(self, item):
        self.table = load()
        return self.table[item]

    def __setitem__(self, key, value):
        self.table = load()
        self.table[key] = value
        update(self.table)

    def __iter__(self):
        self.table = load()
        return iter(self.table)

    def __len__(self):
        self.table = load()
        return len(self.table)

    def items(self):
        self.table = load()
        return self.table.items()

    def keys(self):
        self.table = load()
        return self.table.keys()

    def values(self):
        self.table = load()
        return self.table.values()


db = Table()
