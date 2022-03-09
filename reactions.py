from replit import db

from discord import Reaction, Emoji, Message, Member, Guild

from config import Key
from battlenet import get_top
from obwrole import give_role, donate_role

from typing import List, Dict

# Key.RXN: {id1: {Key.TIME: tm1, Key.SCORE: sc1}}


async def update_top(guild: Guild, member: Member, disc: str):
    top_user = get_top()
    if db[Key.MMBR][top_user][Key.SCORE] < db[Key.MMBR][disc][Key.SCORE]:
        former = guild.get_member_named(top_user)
        if former is None:
            await give_role(guild, member, )
        else:
            await donate_role(guild, former, member, )


async def add_message(guild: Guild, member: Member, message: Message):
    score_given, score = get_score(message)

    if score_given:
        disc = str(member)
        if len(db[Key.MMBR][disc][Key.RXN]) >= nmessages:
            pop_reaction(disc)

        db[Key.MMBR][disc][Key.SCORE] += score
        add_index(disc, message, score)
        await update_top(guild, member, disc)


async def update_message(guild: Guild, member: Member, before: Message, after: Message):
    disc = str(member)
    score_given, score = get_score(after)
    if score_given:
        if before.id in db[Key.MMBR][disc][Key.RXN]:
            bscore = db[Key.MMBR][disc][Key.RXN][before.id][Key.SCORE]
            if score != bscore:
                db[Key.MMBR][disc][Key.SCORE] -= bscore
                del db[Key.MMBR][disc][Key.RXN][before.id]
        elif len(db[Key.MMBR][disc][Key.RXN]) >= nmessages:
            pop_reaction(disc)

        db[Key.MMBR][disc][Key.SCORE] += score
        add_index(disc, after, score)
        await update_top(guild, member, disc)
