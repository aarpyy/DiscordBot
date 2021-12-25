# Class for constant database keys to prevent typos in keys that are not user dependant
class KEYS:
    # Indices for...
    PRIM = "primary"        # discord user's primary battlenet
    ALL = "all"             # dict of all user's battlenets
    BNET = "battlenets"     # list of all battlenets
    MMBR = "members"        # dict of members
    STAT = "stats"          # battlenet specific stats
    PRIV = "private"        # if battlenet is private
    ACTIVE = "active"       # if battlenet is active (only False right before removal)
    ID = "id"               # discord user's ID
    RANK = "ranks"          # battlenet's rank
    ROLE = "roles"          # roles associated with battlenet
    PTFM = "platform"       # battlenet platform
    CTG = "categories"      # PlayOverwatch data categories


bot_role_prefix = "--"
