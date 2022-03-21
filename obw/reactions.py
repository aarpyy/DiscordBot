from replit import db

from discord import Reaction, Emoji, Message, Member, Guild

from .db_keys import *
from .battlenet import path_get_top
from .obwrole import give_role, donate_role

from typing import List, Dict

# RXN: {id1: {TIME: tm1, SCORE: sc1}}


async def update_top(guild: Guild, member: Member, disc: str):
    top_user = path_get_top()
    if db[MMBR][top_user][SCORE] < db[MMBR][disc][SCORE]:
        former = guild.path_get_member_named(top_user)
        if former is None:
            await give_role(guild, member, )
        else:
            await donate_role(guild, former, member, )


async def add_message(guild: Guild, member: Member, message: Message):
    score_given, score = path_get_score(message)

    if score_given:
        disc = str(member)
        if len(db[MMBR][disc][RXN]) >= nmessages:
            pop_reaction(disc)

        db[MMBR][disc][SCORE] += score
        add_index(disc, message, score)
        await update_top(guild, member, disc)


async def update_message(guild: Guild, member: Member, before: Message, after: Message):
    disc = str(member)
    score_given, score = path_get_score(after)
    if score_given:
        if before.id in db[MMBR][disc][RXN]:
            bscore = db[MMBR][disc][RXN][before.id][SCORE]
            if score != bscore:
                db[MMBR][disc][SCORE] -= bscore
                del db[MMBR][disc][RXN][before.id]
        elif len(db[MMBR][disc][RXN]) >= nmessages:
            pop_reaction(disc)

        db[MMBR][disc][SCORE] += score
        add_index(disc, after, score)
        await update_top(guild, member, disc)
