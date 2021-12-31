from replit import db

from discord import Reaction, Emoji, Message, Member, Guild

from config import KEYS, reaction_scores, nmessages
from battlenet import get_top
from obwrole import make_top, change_top

from typing import List, Dict

# KEYS.RXN: {id1: {KEYS.TIME: tm1, KEYS.SCORE: sc1}}


def add_index(disc: str, message: Message, score: int):
    db[KEYS.MMBR][disc][KEYS.RXN][message.id] = {KEYS.TIME: message.created_at.timestamp(), KEYS.SCORE: score}


def get_score(message: Message):
    reactions = message.reactions  # type: List[Reaction]
    score = 0
    score_given = False
    for rxn in reactions:
        if rxn.custom_emoji:
            emoji = rxn.emoji
            if isinstance(emoji, Emoji) and emoji.name in reaction_scores:
                score += reaction_scores[emoji.name] * rxn.count
                score_given = True

    return score_given, score


def pop_reaction(disc: str) -> Dict[str, int]:
    """
    Pops the oldest message user received a reaction to.

    :param disc: username
    :return: reaction index
    """

    oldest_id = max(db[KEYS.MMBR][disc][KEYS.RXN], key=lambda x: db[KEYS.MMBR][disc][KEYS.RXN][x][KEYS.TIME])
    index = db[KEYS.MMBR][disc][KEYS.RXN][oldest_id]
    del db[KEYS.MMBR][disc][KEYS.RXN][oldest_id]
    return index


async def update_top(guild: Guild, member: Member, disc: str):
    top_user = get_top()
    if db[KEYS.MMBR][top_user][KEYS.SCORE] < db[KEYS.MMBR][disc][KEYS.SCORE]:
        former = guild.get_member_named(top_user)
        if former is None:
            await make_top(guild, member)
        else:
            await change_top(guild, former, member)


async def add_message(guild: Guild, member: Member, message: Message):
    score_given, score = get_score(message)

    if score_given:
        disc = str(member)
        if len(db[KEYS.MMBR][disc][KEYS.RXN]) >= nmessages:
            pop_reaction(disc)

        db[KEYS.MMBR][disc][KEYS.SCORE] += score
        add_index(disc, message, score)
        await update_top(guild, member, disc)


async def update_message(guild: Guild, member: Member, before: Message, after: Message):
    disc = str(member)
    score_given, score = get_score(after)
    if score_given:
        if before.id in db[KEYS.MMBR][disc][KEYS.RXN]:
            bscore = db[KEYS.MMBR][disc][KEYS.RXN][before.id][KEYS.SCORE]
            if score != bscore:
                db[KEYS.MMBR][disc][KEYS.SCORE] -= bscore
                del db[KEYS.MMBR][disc][KEYS.RXN][before.id]
        elif len(db[KEYS.MMBR][disc][KEYS.RXN]) >= nmessages:
            pop_reaction(disc)

        db[KEYS.MMBR][disc][KEYS.SCORE] += score
        add_index(disc, after, score)
        await update_top(guild, member, disc)
