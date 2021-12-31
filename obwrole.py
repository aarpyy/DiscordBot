from replit import db

from discord import Guild, Member, Role, Forbidden, HTTPException, utils, Colour
from collections import deque

from config import KEYS
from tools import getkey, loudprint
from battlenet import is_active, is_hidden

from typing import Optional, Set, Union

categ_short = {"Win Percentage": "W"}
categ_major = ("Win Percentage", "Time Played")

mention_tag = "@m"
no_tag = "--"

shitpost_rname = "Top Shitposter"

obw_color = Colour.from_rgb(143, 33, 23)


def gettime(stat: int) -> str:
    hms = deque()
    for _ in range(3):
        stat, value = divmod(stat, 60)
        hms.appendleft(value)

    for v, u in zip(hms, ("h", "m", "s")):
        if v:
            return str(v) + u
    return "0s"


def getstat(ctg: str, stat: Union[int, float, str]) -> str:
    if isinstance(stat, float):
        return str(stat)
    elif isinstance(stat, str):
        return stat
    elif ctg == "Time Played":
        return gettime(stat)
    elif "Accuracy" in ctg or "Percentage" in ctg:
        return str(stat) + '%'
    else:
        return str(stat)


def rolename(role: Role) -> str:
    if role.mentionable:
        return mention_tag + str(role)
    else:
        return no_tag + str(role)


async def globaldel(role: Role, rname: str = None) -> None:
    if rname is None:
        rname = rolename(role)

    globalrm(rname)
    await role.delete()


def globalrm(role: str) -> None:
    for disc in db[KEYS.MMBR]:
        remove(disc, role)
    del db[KEYS.ROLE][role]


def remove(disc: str, role: str) -> None:
    for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
        db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(
            r for r in db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] if r != role)


def rename(before: str, after: str) -> None:
    for disc in db[KEYS.MMBR]:
        for bnet in db[KEYS.MMBR][disc][KEYS.BNET]:
            roles = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE]
            updated = list(after if role == before else role for role in roles)
            db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = updated


async def make_top(gld: Guild, member: Member) -> None:
    shitpost_role = await get(gld, shitpost_rname)
    if shitpost_role is None:
        shitpost_role = await gld.create_role(name=shitpost_rname, mentionable=True, color=obw_color)
    await member.add_roles(shitpost_role)


async def change_top(gld: Guild, former: Member, new: Member) -> None:
    shitpost_role = await get(gld, shitpost_rname)
    if shitpost_role is not None:
        await former.remove_roles(shitpost_role)
    else:
        shitpost_role = await gld.create_role(name=shitpost_rname, mentionable=True, color=obw_color)
    await new.add_roles(shitpost_role)


def get_bnet_roles(disc: str, bnet: str) -> Set[str]:
    """
    Gets all roles associated with given battlenet based on stats.

    :param disc: discord username
    :param bnet: battlenet
    :return: set of roles as strings
    """

    roles = set()  # Empty set for roles

    # Table of battlenet's statistics; KEYS.STAT will always exist, but could be empty dict
    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.STAT].get("quickplay", {})

    # For each stat associated with battlenet, add that stat if it is an important one
    for ctg in table:
        if ctg in categ_major:
            hero = max(table[ctg], key=lambda x: table[ctg][x])
            roles.add(f"{no_tag}{hero}-{getstat(ctg, table[ctg][hero])}" + categ_short.get(ctg, ""))

    table = db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.RANK]  # Table of battlenet's competitive ranks
    rank = max(table, key=lambda x: table[x])
    roles.add(f"{no_tag}{rank.capitalize()}-{table[rank]}")

    if is_active(disc, bnet):
        roles.add(mention_tag + bnet)
        roles.add(mention_tag + db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.PTFM])
    return roles


async def get(gld: Guild, role: str) -> Optional[Role]:
    """
    Helper function that more sufficiently ensures that the Role is returned if it exists. First, it
    checks if the Role is already in the db, getting the Role via Role.id if true. Otherwise,
    it iterates through all Roles in Guild, attempting to match via string, returning None if no
    matches were made.

    :param gld: Guild
    :param role: name of role
    :return: Optional[Role]
    """

    if role in db[KEYS.ROLE]:
        return gld.get_role(db[KEYS.ROLE][role][KEYS.ID])
    else:
        try:
            roles = await gld.fetch_roles()
        except HTTPException:
            return None
        else:
            role = role[2:]
            role_obj = utils.find(lambda rle: rle.name == role, roles)
            if role_obj is not None:
                db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}
            return role_obj


async def update(gld: Guild, disc: str, bnet: str) -> None:
    """
    Gives Guild Member Role objects based off of the stats retrieved from connected battlenet.

    :param gld: Guild that the discord user belongs to
    :param disc: Discord username
    :param bnet: Linked battlenet
    :raises AttributeError: If Bot lacks access to Guild
    :raises ValueError: If Discord API unable to fetch Member
    :return: None
    """

    loudprint(f"Updating roles for {disc}[{bnet}]...")

    if is_hidden(disc, bnet):
        loudprint(f"{disc}[{bnet}] is hidden. No roles given")
        return

    user_id = db[KEYS.MMBR][disc][KEYS.ID]

    # Use Guild.fetch_member() to ensure that even if member not in cache they are retrieved
    try:
        member = await gld.fetch_member(user_id)  # type: Member
    except Forbidden as src:
        raise AttributeError(f"Unable to access Guild {str(gld)}") from src
    except HTTPException as src:
        raise ValueError(f"Fetching user {disc} <id={user_id}> failed") from src

    loudprint(f"Member fetched: {str(member)} ({member.id})")

    # To calculate roles to add, first get all roles that this battlenet should have, then subtract the roles
    # from that set that the user already has

    role: Role
    current_discord_roles = set(rolename(role) for role in member.roles)
    new_bnet_roles = get_bnet_roles(disc, bnet)
    current_bnet_roles = set(db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE])
    to_add = new_bnet_roles.difference(current_discord_roles)

    loudprint(f"Roles in to_add: {to_add}")

    # To calculate roles to remove, get all roles that the user currently has minus the roles that they are
    # going to have after the update. The intersection of this set with all roles that the discord user
    # actually has returns the roles that the user has in discord that should be removed. This set
    # now needs to be cross referenced with all the other linked battlenets for this discord user, since
    # if two battlenets give the user the same role, if one battlenet removes the role the user should
    # still keep the role.

    to_remove = (current_bnet_roles - new_bnet_roles) & current_discord_roles
    for b in db[KEYS.MMBR][disc][KEYS.BNET]:
        if b != bnet:
            to_remove -= set(db[KEYS.MMBR][disc][KEYS.BNET][b][KEYS.ROLE])

    roles_lost = current_bnet_roles - new_bnet_roles

    loudprint(f"Roles in to_remove: {to_remove}")

    # Don't increment member count for any roles in to_add, since these are not all the roles that need to be
    # incremented. Instead, take care of adding and removing of actual roles/entrance into db and later
    # increment all roles being added directly to user regardless of if the role was just created
    for role in to_add:  # type: str
        role_obj = await get(gld, role)
        if role_obj is None:
            if role.startswith(mention_tag):
                role_obj = await gld.create_role(name=role[2:], mentionable=True, color=obw_color)
            else:
                role_obj = await gld.create_role(name=role[2:], color=obw_color)

            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: 0}

        elif role not in db[KEYS.ROLE]:
            db[KEYS.ROLE][role] = {KEYS.ID: role_obj.id, KEYS.MMBR: len(role_obj.members)}

        await member.add_roles(role_obj)

    for role in new_bnet_roles:
        db[KEYS.ROLE][role][KEYS.MMBR] += 1

    for role in roles_lost:
        db[KEYS.ROLE][role][KEYS.MMBR] -= 1

    for role in to_remove:  # type: str
        role_obj = await get(gld, role)  # type: Role
        if role_obj is None:
            continue

        await member.remove_roles(role_obj)

        if not db[KEYS.ROLE][role][KEYS.MMBR]:  # If just removed last member, delete the Role
            loudprint(f"Deleting {str(role_obj)}; Role.members: {[str(m) for m in role_obj.members]}; "
                      f"db: {db[KEYS.ROLE][role][KEYS.MMBR]}")
            await globaldel(role_obj, role)

    db[KEYS.MMBR][disc][KEYS.BNET][bnet][KEYS.ROLE] = list(new_bnet_roles)
